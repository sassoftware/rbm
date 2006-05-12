from raa.modules.raasrvplugin import rAASrvPlugin
from conary.repository.netrepos.netserver import ServerConfig
from conary.repository.netrepos.netserver import NetworkRepositoryServer
from conary.lib.cfgtypes import CfgEnvironmentError

class MirrorUsers(rAASrvPlugin):
    def doTask(self, schedId, execId):
        '''
            Updates serverName in conaryCNR if no commits have occured in the
            repository.
        '''
        cnrPath ='/srv/conary/repository.cnr'

        data = self.server.getData()
        self.server.clearData()

        cfg = ServerConfig()
        cfg.read(cnrPath)
        nr = NetworkRepositoryServer(cfg, 'localhost')

        if data[0]['operation'] == 'list':
            users =  nr.auth.userAuth.getUserList()
            for usr in users:
                if usr != 'admin' and usr != 'anonymous':
                    mirrorPerm = 'No'
                    for x in nr.auth.userAuth.getGroupsByUser(usr):
                        if nr.auth.groupCanMirror(x):
                            mirrorPerm = 'Yes'
                            break
                    self.server.setData(usr, mirrorPerm)
        elif data[0]['operation'] == 'add':
            nr.auth.addUser(data[0]['user'], data[0]['password'])
            nr.auth.addAcl(data[0]['user'], None, None, True,
                                 False, False)
            nr.auth.setMirror(data[0]['user'], True)
        elif data[0]['operation'] == 'mirror':
            for x in nr.auth.userAuth.getGroupsByUser(data[0]['user']):
                nr.auth.setMirror(data[0]['user'], 
                                  not nr.auth.groupCanMirror(x))
        elif data[0]['operation'] == 'delete':
            nr.auth.deleteUserByName(data[0]['user'])
        elif data[0]['operation'] == 'pass':
            nr.auth.changePassword(data[0]['user'], data[0]['password'])
