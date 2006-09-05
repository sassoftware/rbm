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
            try:
                cfg.display(f)
            finally:
                f.close()
        except IOError:
            pass

        pipeCmd = os.popen('hostname --fqdn')
        try:
            srvName = pipeCmd.read().strip()
        finally:
            pipeCmd.close()

        cfgData = '\n'.join(['repositoryMap %s http://%s/conary/' % (x, srvName) for x in data if x != 'localhost'])
        cfgData = cfgData and (cfgData + '\n') or cfgData
        f = open('/srv/www/html/conaryrc', 'w')
        try:
            f.write(cfgData)
        finally:
            f.close()

        try:
            os.system(apacheRestart)
        except:
            pass
