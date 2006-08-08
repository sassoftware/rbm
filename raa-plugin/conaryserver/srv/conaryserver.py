#
# Copyright (c) 2005-2006 rPath, Inc.
#
# All rights reserved
#

import os
from raa.modules.raasrvplugin import rAASrvPlugin
from conary.repository.netrepos.netserver import ServerConfig
from conary.lib.cfgtypes import CfgEnvironmentError

class ConaryServer(rAASrvPlugin):
    def doTask(self, schedId, execId):
        '''
            Updates serverName in conaryCNR if no commits have occured in the
            repository.
        '''

        cnrPath = '/srv/conary/repository.cnr'
        apacheRestart = '/usr/bin/killall -USR1 httpd'
        data = self.server.getData()
        if not len(data):
            data = ('localhost',)
        try:
            cfg = ServerConfig()
            cfg.read(cnrPath)
            cfg.serverName = data
        except CfgEnvironmentError:
            pass

        try:
            f = open(cnrPath, "w")
            cfg.display(f)
            f.close()
        except IOError:
            pass

        try:
            os.system(apacheRestart)
        except:
            pass
