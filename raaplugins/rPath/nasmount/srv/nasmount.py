#
# Copyright (c) 2007 rPath, Inc.
#
# All rights reserved
#

import os
import socket
import tempfile

from raa.modules.raasrvplugin import rAASrvPlugin
from raaplugins.backup import lib
from raa.lib import mount

from conary.lib import util

def isMounted(mnt):
    p = os.popen('mount | grep "%s"' % mnt)
    p.read()
    res = p.close()
    return not res

SEEK_SET, SEEK_CUR, SEEK_END = range(0, 3)
NFS_PROTO = 2049

def catchExceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return False, func(*args, **kwargs)
        except Exception, e:
            return True, str(e)
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    return wrapper


class NasMount(rAASrvPlugin):
    def mkFstabEntry(self, server, remoteMount, mountPoint):
        assert os.path.exists('/etc/fstab'), "/etc/fstab does not exist"

        entry = "%s:%s %s nfs defaults 0 0\n" % \
            (server, remoteMount, mountPoint)

        f = open('/etc/fstab', 'r+')
        data = f.read()

        assert '%s:%s' % (server, remoteMount) not in data, \
            "Remote Mount: %s:%s is already present in /etc/fstab" % \
            (server, remoteMount)
        assert mountPoint not in data, "Local Mount: %s already in /etc/fstab"

        if data[-1] != '\n':
            entry = '\n' + entry

        f.seek(0, SEEK_END)
        f.write(entry)
        f.close()

    @catchExceptions
    def setMount(self, schedId, execId, server, remoteMount, mountPoint):
        assert os.path.exists(mountPoint), \
            "Mount Point: %s does not exist" % mountPoint
        assert not isMounted(mountPoint), "%s is already mounted" % mountPoint
        assert not isMounted(remoteMount), "%s is already mounted" % remoteMount
        assert not os.listdir(mountPoint), "%s is not empty" % mountPoint

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((server, NFS_PROTO))
        s.close()

        # a colon in a mount point implies NFS
        mount.mount('%s:%s' % (server, remoteMount), mountPoint)

        try:
            fd, tmpFile = tempfile.mkstemp(dir = mountPoint)
        finally:
            if 'fd' in locals():
                os.close(fd)
                os.unlink(tmpFile)
        # make fstab entry
        self.mkFstabEntry(server, remoteMount, mountPoint)
        return ''

    @catchExceptions
    def getMount(self, schedId, execId, mountPoint):
        f = open('/etc/fstab')
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
