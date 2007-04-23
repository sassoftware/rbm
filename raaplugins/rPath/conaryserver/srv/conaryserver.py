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
    generatedFile = '/srv/conary/repository-generated.cnr'
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
            cfg.read(self.generatedFile, exception=False)
            cfg.serverName = data
        except CfgEnvironmentError:
            pass

        try:
            genFile = open(self.generatedFile, 'w')
            try:
                displayKeys = [x for x in cfg.keys() if x == 'serverName' or not cfg.isDefault(x)]
                for x in displayKeys:
                    cfg.displayKey(x, out=genFile)
            finally:
                genFile.close()
        except IOError, e:
            pass

        pipeCmd = os.popen('hostname --fqdn')
        try:
            srvName = pipeCmd.read().strip()
        finally:
            pipeCmd.close()

        cfg = ServerConfig()
        cfg.read(self.cnrPath)
        if cfg.forceSSL:
            protocol = 'https'
        else:
            protocol = 'http'

        cfgData = '\n'.join(['repositoryMap %s %s://%s/conary/' % (x, protocol, srvName) for x in data if x != 'localhost'])
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
