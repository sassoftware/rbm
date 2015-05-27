#!/usr/bin/python
#
# Copyright (c) SAS Institute Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
if not cfg.repositoryDB:
    print "In proxy mode, no migration required"
    sys.exit(0)

tracelog.FileLog = SimpleFileLog
tracelog.initLog(filename='stderr', level=2)

db = dbstore.connect(cfg.repositoryDB[1], cfg.repositoryDB[0])
schema.loadSchema(db, doMigrate=True)
if cfg.repositoryDB[0] == 'sqlite':
    os.chown(cfg.repositoryDB[1], pwd.getpwnam('apache')[2], 
             pwd.getpwnam('apache')[3])
