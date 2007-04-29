#
# Copyright (c) 2007 rPath, Inc.
#
# All rights reserved
#

import os
import pwd
import re
import socket
import tempfile

from raa.modules.raasrvplugin import rAASrvPlugin
from raaplugins.backup import lib
from raa.lib import mount

from conary.lib import util

import logging
log = logging.getLogger('raa.nasmount')

def isMounted(mnt):
    p = os.popen('mount | grep "%s"' % mnt)
    p.read()
    res = p.close()
    return not res

SEEK_SET, SEEK_CUR, SEEK_END = range(0, 3)

FSTAB = '/etc/fstab'

mountOptions = ['tcp', 'rw', 'hard', 'intr', 'rsize=32768', 'wsize=32768']

def catchExceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return False, func(*args, **kwargs)
        except Exception, e:
            return True, str(e)
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    return wrapper

def scrubInput(regex, input, errMessage):
    assert re.match(regex, input), errMessage % input

E_CANT_CREATE, E_CANT_DELETE, E_NO_USER = range(1, 4)

def testTouchFile(path):
    pid = os.fork()
    if not pid:
        try:
            log.info("switching to apache user")
            apacheUid, apacheGid = pwd.getpwnam('apache')[2:4]
            os.setgid(apacheGid)
            os.setuid(apacheUid)
            try:
                log.info("attempting to create test file")
                fd, filePath = tempfile.mkstemp(dir = path)
            except:
                log.error("could not create test file")
                os._exit(E_CANT_CREATE)
            else:
                log.info("created test file. attempting to delete")
                os.close(fd)
                try:
                    os.unlink(filePath)
                except:
                    log.error("couldn't delete test file")
                    os._exit(E_CANT_DELETE)
        except KeyError, e:
            if 'name not found' in str(e):
                log.error("apache user doesn't exist")
                os._exit(E_NO_USER)
            else:
                raise
        else:
            log.info("file creation test passed")
            os._exit(0)
    pid, exitStatus = os.waitpid(pid, 0)
    exitCode = os.WEXITSTATUS(exitStatus)
    exitMessages = {0: (False, ''),
                    E_CANT_CREATE: (True, 'Apache user cannot create files'),
                    E_CANT_DELETE: (True, 'Apache user cannot delete files'),
                    E_NO_USER: (True, "Apache user doesn't exist")}
    return exitMessages.get( \
        exitCode,
        (True, 'Unknown Error occured while testing remote file access'))


class NasMount(rAASrvPlugin):
    def mkFstabEntry(self, server, remoteMount, mountPoint):
        assert os.path.exists(FSTAB), "/etc/fstab does not exist"

        entry = "%s:%s %s nfs %s 0 0\n" % \
            (server, remoteMount, mountPoint, ','.join(mountOptions))

        f = open(FSTAB, 'r+')
        data = f.read()

        assert '%s:%s' % (server, remoteMount) not in data, \
            "Remote Mount: %s:%s is already present in /etc/fstab" % \
            (server, remoteMount)
        assert mountPoint not in data, \
            "Local Mount: %s already in /etc/fstab" % mountPoint

        if data and data[-1] != '\n':
            entry = '\n' + entry

        log.info('modifying /etc/fstab')
        f.seek(0, SEEK_END)
        f.write(entry)
        f.close()
        log.info('/etc/fstab written')

    @catchExceptions
    def setMount(self, schedId, execId, server, remoteMount, mountPoint):
        scrubInput('[A-Za-z0-9\.-]*$', server, "'%s' must be a FQDN")

        scrubInput('[^\'";<>&|!$]*$', remoteMount,
                   "'%s' cannot contain string or shell delimiters")

        assert os.path.exists(mountPoint), \
            "Mount Point: %s does not exist" % mountPoint
        assert not isMounted(remoteMount), "%s is already mounted" % remoteMount
        assert not isMounted(mountPoint), "%s is already mounted" % mountPoint
        assert not os.listdir(mountPoint), "%s is not empty" % mountPoint

        log.info('attempting to mount %s' % mountPoint)
        # a colon in a mount point implies NFS
        mount.mount('%s:%s' % (server, remoteMount), mountPoint,
                    options = mountOptions)

        try:
            errState, msg = testTouchFile(mountPoint)
            if errState:
                try:
                    apacheUid, apacheGid = pwd.getpwnam('apache')[2:4]
                    os.chown(mountPoint, apacheUid, apacheGid)
                except:
                    # already an error state, so nothing's being masked
                    pass
                else:
                    errState, msg = testTouchFile(mountPoint)

            assert not errState, msg

        # make fstab entry
            self.mkFstabEntry(server, remoteMount, mountPoint)
            return ''
        except:
            mount.umount_point(mountPoint)
            raise

    @catchExceptions
    def getMount(self, schedId, execId, mountPoint):
        f = open(FSTAB)
        data = f.readlines()
        mountLines = [x for x in data if mountPoint in x]
        if not mountLines:
            return '', ''
        mnt = mountLines[0].split()[0]
        if ':' in mnt:
            server, mnt = mnt.split(':')
        else:
            server = ''
        return server, mnt

    def doTask(self, *args, **kwargs):
        pass
