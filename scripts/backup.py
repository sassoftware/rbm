#!/usr/bin/python

import os
import pwd
import shutil
import sys
import fcntl

dbPath = os.path.join(os.path.sep, 'srv', 'conary', 'sqldb')
tmpDbPath = dbPath + '-tmp'

class DBLock(object):
    def __init__(self, path):
        self.path = path

    def acquire(self):
        self.file = open(self.path, 'r+')
        fcntl.lockf(self.file.fileno(), fcntl.LOCK_EX)

    def release(self):
        self.file.close()

def clean():
    if os.path.exists(tmpDbPath):
        os.unlink(tmpDbPath)

def backup(out = sys.stdout):
    print >> out, os.path.join(os.path.sep, 'etc', 'fstab')
    for bkpFile in ('conaryver', 'repository.cnr', 'repository-custom.cnr',
                    'repository-generated.cnr', 'logs'):
        print >> out, os.path.join(os.path.sep, 'srv', 'conary', bkpFile)

    # now back up the sqldb
    dbLock = DBLock(dbPath)
    dbLock.acquire()
    try:
        shutil.copy(dbPath, tmpDbPath)
    finally:
        dbLock.release()
    print >> out, tmpDbPath

def restore():
    shutil.move(tmpDbPath, dbPath)

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
    apacheUID, apacheGID = pwd.getpwnam('apache')[2:4]
    os.setgid(apacheGID)
    os.setuid(apacheUID)
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
