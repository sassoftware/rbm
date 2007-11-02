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

cnrPath = '/srv/conary/repository.cnr'

cfg = ServerConfig()

try:
    cfg.read(cnrPath)
except cfgtypes.CfgEnvironmentError:
    print "Error reading %s" % cnrPath
    sys.exit(1)

db = dbstore.connect(cfg.repositoryDB[1], cfg.repositoryDB[0])
schema.loadSchema(db)
if cfg.repositoryDB[0] == 'sqlite':
    os.chown(cfg.repositoryDB[1], pwd.getpwnam('apache')[2], 
             pwd.getpwnam('apache')[3])
