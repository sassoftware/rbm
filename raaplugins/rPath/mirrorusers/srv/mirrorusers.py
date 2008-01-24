#
# Copyright (c) 2005-2006 rPath, Inc.
#
# All rights reserved
#

from raa.modules.raasrvplugin import rAASrvPlugin
from conary.repository.netrepos.netserver import ServerConfig
from conary.repository.netrepos.netserver import NetworkRepositoryServer
from conary.repository import errors

class MirrorUsers(rAASrvPlugin):
    cnrPath ='/srv/conary/repository.cnr'
    def _getNetworkRepo(self):
        cfg = ServerConfig()
        cfg.read(self.cnrPath)
        nr = NetworkRepositoryServer(cfg, 'localhost')
        return nr

    def getUserList(self, schedId, execId):
        nr = self._getNetworkRepo()
        users =  nr.auth.userAuth.getUserList()
        ret = []
        for usr in users:
            perm = 'Other'
            for x in nr.auth.userAuth.getRolesByUser(usr):
                # anonymous user
                if x == 'anonymous':
                    perm = 'Anonymous'
                    break
                perms = nr.auth.iterPermsByRole(x)
                for i in perms:
                    # admin user
                    if nr.auth.roleIsAdmin(x) and \
                            i == ('ALL', 'ALL', 1, 0):
                        perm = 'Admin'
                        break
                    # mirror user
                    elif nr.auth.roleCanMirror(x) and \
                            i == ('ALL', 'ALL', 1, 1):
                        perm = 'Mirroring'
                        break
            ret.append({'user' : usr, 'permission' : perm})
        return ret
    
    def addUser(self, schedId, execId, user, password, permission):
        nr = self._getNetworkRepo()
        if permission == 'Mirror':
            write = True
            mirror = True
            admin = False
            remove = True
        elif permission == 'Anonymous':
            write = False
            mirror = False
            admin = False
            remove = False
        elif permission == 'Admin':
            write = True
            mirror = False
            admin = True
            remove = False
        try:
            nr.auth.addUser(user, password)
            nr.auth.addAcl(user, None, None, write=write, remove=remove)
            nr.auth.setAdmin(user, admin)
            nr.auth.setMirror(user, mirror)
        except errors.RoleAlreadyExists:
            return False
        return True

    def deleteUser(self, schedId, execId, user):
        nr = self._getNetworkRepo()
        nr.auth.deleteUserByName(user)
        return True

    def changePassword(self, schedId, execId, user, newPass):
        nr = self._getNetworkRepo()
        nr.auth.changePassword(user, newPass)
        return True
