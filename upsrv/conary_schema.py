#!/usr/bin/python
#
# Copyright (c) SAS Institute Inc.
#

import sys
import os
import pwd
from conary.server import schema
from conary.lib import cfgtypes, tracelog
from conary import dbstore

from .config import UpsrvConfig

class SimpleFileLog(tracelog.FileLog):
    def printLog(self, level, msg):
        self.fd.write("%s\n" % msg)

try:
    cfg = UpsrvConfig.load()
except cfgtypes.CfgEnvironmentError:
    print "Error reading config file"
    sys.exit(1)

tracelog.FileLog = SimpleFileLog
tracelog.initLog(filename='stderr', level=2)

db = dbstore.connect(cfg.repositoryDB[1], cfg.repositoryDB[0])
schema.loadSchema(db, doMigrate=True)
if cfg.repositoryDB[0] == 'sqlite':
    os.chown(cfg.repositoryDB[1], pwd.getpwnam('apache')[2], 
             pwd.getpwnam('apache')[3])
