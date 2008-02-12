#!/usr/bin/python

import os
import pwd
import re
import shutil
import sys
import fcntl

dbPath = os.path.join(os.path.sep, 'srv', 'conary', 'sqldb')
tmpDbPath = dbPath + '-tmp'
tmpFsPath = os.path.join(os.path.sep, 'srv', 'conary', 'fstab')
apacheUID, apacheGID = pwd.getpwnam('apache')[2:4]

class DBLock(object):
    def __init__(self, path):
        self.path = path

    def acquire(self):
        self.file = open(self.path, 'r+')
        fcntl.lockf(self.file.fileno(), fcntl.LOCK_EX)

    def release(self):
        self.file.close()

def clean():
    for path in (tmpDbPath, tmpFsPath):
        if os.path.exists(path):
            os.unlink(path)

def backup(out = sys.stdout):
    for bkpFile in ('conaryver', 'repository.cnr', 'config/*',
                    'logs'):
        print >> out, os.path.join(os.path.sep, 'srv', 'conary', bkpFile)

    # now back up any programmaticly changed lines from /etc/fstab
    try:
        f = open(os.path.join(os.path.sep, 'etc', 'fstab'))
    except IOError:
        fsData = ''
    else:
        fsData = f.read()
        f.close()

    entry = re.findall('.*\s/srv/conary/contents\s.*', fsData)
    entry = entry and entry[0] or ''
    f = open(tmpFsPath, 'w')
    f.write(entry)
    f.close()
    print >> out, tmpFsPath
    os.chown(tmpFsPath, apacheUID, apacheGID)

    # now back up the sqldb
    ### TODO: Fix this for postgresql support
    dbLock = DBLock(dbPath)
    dbLock.acquire()
    try:
        shutil.copy(dbPath, tmpDbPath)
    finally:
        dbLock.release()
    print >> out, tmpDbPath
    os.chown(tmpDbPath, apacheUID, apacheGID)

def restore():
    ### TODO: Fix this for postgresql support
    shutil.move(tmpDbPath, dbPath)
    os.chown(dbPath, apacheUID, apacheGID)
    f = open(tmpFsPath)
    entry = f.read()
    f.close()
    if entry:
        f = open(os.path.join(os.path.sep, 'etc', 'fstab'), 'r+')
        data = f.read()
        if not re.findall('.*\s/srv/conary/contents\s.*', data):
            if data and data[-1] != '\n':
                entry = '\n' + entry
            if entry[-1] != '\n':
                entry += '\n'

            f.write(entry)
        f.close()

def handle(func, *args, **kwargs):
    errno = 0
    try:
        func(*args, **kwargs)
    except:
        exception, e, bt = sys.exc_info()
        if exception in (OSError, IOError):
            errno = e.errno
        else:
            errno = 1
        import traceback
        print >> sys.stderr, ''.join(traceback.format_tb(bt))
        print >> sys.stderr, exception, e
    sys.exit(errno)

def usage(out = sys.stderr):
    print >> out, sys.argv[0] + ":"
    print >> out, "    [b/backup]: back up databases and issue manifest."
    print >> out, "    [r/restore]: restore databases."
    print >> out, "    [c/clean]: clean up temporary files used during backup."

def main(argv = sys.argv[1:]):
    mode = (len(sys.argv) > 1) and sys.argv[1] or ''
    if mode in ('r', 'restore'):
        sys.exit(handle(restore))
    elif mode in ('b', 'backup'):
        sys.exit(handle(backup, sys.stdout))
    elif mode in ('c', 'clean'):
        sys.exit(handle(clean))
    elif mode.upper() in ('?', 'H', 'HELP'):
        usage(out = sys.stdout)
    else:
        usage()

if __name__ == '__main__':
    main()
