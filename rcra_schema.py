#!/usr/bin/python

# Copyright (c) 2006 rPath, Inc
# All rights reserved

import sys
import os
import pwd
from conary.server import schema
from conary.lib import cfgtypes
from conary.repository.netrepos.netserver import ServerConfig
from conary import dbstore

def usage():
    print 'usage: %s {init|update}' % sys.argv[0]
    sys.exit(0)

def updateSchema(cfg):
    db = dbstore.connect(cfg.repositoryDB[1], cfg.repositoryDB[0])
    schema.loadSchema(db)

if len(sys.argv) != 2:
    usage()

cnrPath = '/srv/conary/repository.cnr'

cfg = ServerConfig()
try:
    cfg.read(cnrPath)
except cfgtypes.CfgEnvironmentError:
    print "Error reading %s" % cnrPath
    sys.exit(1)

if sys.argv[1] == 'init':
    updateSchema(cfg)
    os.chown(cfg.repositoryDB[1], pwd.getpwnam('apache')[2], 
             pwd.getpwnam('apache')[3])
elif sys.argv[1] == 'update':
    updateSchema(cfg)
else:
    usage()
