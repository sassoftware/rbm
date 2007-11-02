#!/usr/bin/python

# Copyright (c) 2006 rPath, Inc
# All rights reserved

import os
import sys
import time

from conary import dbstore
from conary.lib import util
from conary.repository.netrepos.netserver import ServerConfig
from conary.server import schema

HTTPD_START = '/etc/init.d/httpd start'
HTTPD_STOP = '/etc/init.d/httpd stop'

cfg = ServerConfig()
cfg.read('/srv/conary/repository.cnr')
if cfg.repositoryDB[0] == 'postgresql':
    print "This Update Service is already using postgresql for its database."
    sys.exit(1)

if cfg.serverName != ['localhost']:
    print "This Update Service is already in use and cannot move to postgres."
    sys.exit(1)

db = dbstore.connect(cfg.repositoryDB[1], cfg.repositoryDB[0])
cu = db.cursor()

cu.execute("SELECT COUNT(*) FROM INSTANCES")

if cu.fetchone()[0] > 0:
    print "Data has already been committed to this repository.  Unable to move to postgres."

print "Executing this script will switch your Update Service's repository database from sqlite to postgresql" 
print "It will be impossible to move back to sqlite after executing this script."
print "are you ABSOLUTELY SURE you want to do this? [yes/N]"
answer = sys.stdin.readline()[:-1]
if answer.upper() != 'YES':
    if answer.upper() not in ('', 'N', 'NO'):
        print >> sys.stderr, "you must type 'yes' if you truly want to move to postgres."
    print >> sys.stderr, "aborting."
    sys.exit(1)

util.execute(HTTPD_STOP)

util.execute('chkconfig postgresql on')
util.execute('/etc/init.d/postgresql start')
time.sleep(4)
util.execute('createlang -U postgres plpgsql template1')
util.execute('psql -U postgres -d postgres -c "CREATE ROLE rapus NOSUPERUSER CREATEDB NOCREATEROLE INHERIT LOGIN;"')
util.execute('psql -U rapus -d postgres -c "CREATE DATABASE rapus ENCODING \'UTF8\';"')

db = dbstore.connect('rapus@localhost.localdomain/rapus', 'postgresql')
schema.loadSchema(db)

fd = open('/srv/conary/repository-generated.cnr', 'w')

cfg.repositoryDB = ('postgresql', 'rapus@localhost.localdomain/rapus')
cfg.displayKey('repositoryDB', out=fd)
fd.close()

util.execute(HTTPD_START)

print "This Update Service appliance is now using postgresql for its database."
