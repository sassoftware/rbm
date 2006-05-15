#!/usr/bin/python

# Copyright (c) 2006 rPath, Inc
# All rights reserved

import sys
import os
import pwd
from conary.server import schema
from conary.lib import cfgtypes
from conary.repository.netrepos.netserver import ServerConfig
from conary.repository.netrepos.netserver import NetworkRepositoryServer
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
    netRepos = NetworkRepositoryServer(cfg, 'http://localhost') 
    # Add admin
    netRepos.auth.addUser('admin', 'admin')
    netRepos.auth.addAcl('admin', None, None, True, False, True)
    netRepos.auth.setMirror('admin', True)
    # Add anonymous
    netRepos.auth.addUser('anonymous', 'anonymous')
    netRepos.auth.addAcl('anonymous', None, None, False, False, False)
    netRepos.auth.setMirror('anonymous', False)
    os.chown(cfg.repositoryDB[1], pwd.getpwnam('apache')[2], 
             pwd.getpwnam('apache')[3])
elif sys.argv[1] == 'update':
    updateSchema(cfg)
else:
    usage()
