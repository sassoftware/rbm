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
    cnrPath = '/srv/conary/repository.cnr'
    conaryrcPath = '/srv/www/html/conaryrc'
    apacheRestart = '/usr/bin/killall -USR1 httpd'

    def doTask(self, schedId, execId):
        '''
            Updates serverName in repository.cnr if no commits have occured in the
            repository.
        '''

        data = self.server.getData()
        if not len(data):
            data = ('localhost',)
        try:
            cfg = ServerConfig()
            cfg.read(self.cnrPath)
            cfg.serverName = data
        except CfgEnvironmentError:
            pass

        try:
            f = open(self.cnrPath, "w")
            try:
                cfg.display(f)
            finally:
                f.close()
        except IOError, e:
            pass

        pipeCmd = os.popen('hostname --fqdn')
        try:
            srvName = pipeCmd.read().strip()
        finally:
            pipeCmd.close()

        cfgData = '\n'.join(['repositoryMap %s http://%s/conary/' % (x, srvName) for x in data if x != 'localhost'])
        cfgData = cfgData and (cfgData + '\n') or cfgData
        f = open(self.conaryrcPath, 'w')
        try:
            f.write(cfgData)
        finally:
            f.close()

        try:
            os.system(self.apacheRestart)
        except:
            pass
