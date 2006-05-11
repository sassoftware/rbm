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
    
        data = self.server.getData()[0]

        try:
            cfg = ServerConfig()
            cfg.read(cnrPath)
            cfg.serverName = data['newsrv']
        except CfgEnvironmentError:
            pass

        try:
            f = open(cnrPath, "w")
            cfg.display(f)
            f.close()
        except IOError:
            pass
