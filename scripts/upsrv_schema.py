#!/usr/bin/python

# Copyright (c) 2006 rPath, Inc
# All rights reserved

import sys
import os
import pwd
from conary.server import schema
from conary.lib import cfgtypes, tracelog
from conary.repository.netrepos.netserver import ServerConfig
from conary import dbstore

class SimpleFileLog(tracelog.FileLog):
    def printLog(self, level, msg):
        self.fd.write("%s\n" % msg)

cnrPath = '/srv/conary/repository.cnr'

cfg = ServerConfig()

tracelog.FileLog = SimpleFileLog
tracelog.initLog(filename='stderr', level=2)

try:
    cfg.read(cnrPath)
except cfgtypes.CfgEnvironmentError:
    print "Error reading %s" % cnrPath
    sys.exit(1)

db = dbstore.connect(cfg.repositoryDB[1], cfg.repositoryDB[0])
schema.loadSchema(db, doMigrate=True)
if cfg.repositoryDB[0] == 'sqlite':
    os.chown(cfg.repositoryDB[1], pwd.getpwnam('apache')[2], 
             pwd.getpwnam('apache')[3])
