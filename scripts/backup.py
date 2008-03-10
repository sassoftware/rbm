#!/usr/bin/python

import os
import pwd
import re
import shutil
import sys
import fcntl

from conary.lib import util
from conary.repository import netserver


dbPath = os.path.join(os.path.sep, 'srv', 'conary', 'sqldb')
tmpDbPath = dbPath + '-tmp'
tmpFsPath = os.path.join(os.path.sep, 'srv', 'conary', 'fstab')
apacheUID, apacheGID = pwd.getpwnam('apache')[2:4]

cfg_path = '/srv/conary/repository.cnr'
pg_dump_path = '/srv/conary/rapus.sql'

class DBLock(object):
    def __init__(self, path):
        self.path = path

    def acquire(self):
        self.file = open(self.path, 'r+')
        fcntl.lockf(self.file.fileno(), fcntl.LOCK_EX)

    def release(self):
        self.file.close()

def clean():
    for path in (tmpDbPath, tmpFsPath, pg_dump_path):
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
    server_cfg = netserver.ServerConfig()
    server_cfg.read(cfg_path)
    rep_driver, rep_path = server_cfg.repositoryDB

    if rep_driver == 'sqlite':
        dbLock = DBLock(dbPath)
        dbLock.acquire()
        try:
            shutil.copy(dbPath, tmpDbPath)
        finally:
            dbLock.release()
        print >> out, tmpDbPath
        os.chown(tmpDbPath, apacheUID, apacheGID)
    elif rep_driver == 'postgresql':
        util.execute('pg_dump -c --disable-triggers rapus >"%s"' % pg_dump_path
        print >> out, pg_dump_path
    else:
        sys.exit("Don't know how to back up a '%s' database!" % rep_driver)

def restore():
    server_cfg = netserver.ServerConfig()
    server_cfg.read(cfg_path)
    rep_driver, rep_path = server_cfg.repositoryDB

    if rep_driver == 'sqlite':
        shutil.move(tmpDbPath, dbPath)
        os.chown(dbPath, apacheUID, apacheGID)
    elif rep_driver == 'postgresql':
        # Try to create needed resources first. This will generally fail since
        # these are created when the database is initialized, but we might
        # be restoring onto a bare database.
        os.system('psql -U postgres -d postgres -c "CREATE ROLE rapus '
            'NOSUPERUSER CREATEDB NOCREATEROLE INHERIT LOGIN;" '
            '>/dev/null 2>&1')
        os.system('psql -U rapus -d postgres -c "CREATE DATABASE rapus '
            'ENCODING \'UTF8\';" >/dev/null 2>&1')
        os.system('createlang -U postgres plpgsql rapus >/dev/null 2>&1')

        # Now do the restore
        util.execute('psql -l <"%s" >/dev/null' % pg_dump_path)
    else:
        sys.exit("Don't know how to restore a '%s' database!" % rep_driver)

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
