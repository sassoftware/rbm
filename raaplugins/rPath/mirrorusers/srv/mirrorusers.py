#
# Copyright (c) 2005-2008 rPath, Inc.
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
            roles = nr.auth.userAuth.getRolesByUser(usr)
            if len(roles) == 1:
                role = roles[0]
                for roleperm in nr.auth.iterPermsByRole(role):
                    # admin user
                    if nr.auth.roleIsAdmin(role) and \
                            roleperm == ('ALL', 'ALL', 1, 0):
                        perm = 'Admin'
                        break
                    # mirror user
                    elif nr.auth.roleCanMirror(role) and \
                            roleperm == ('ALL', 'ALL', 1, 1):
                        perm = 'Mirroring'
                        break
                # anonymous user
                if role == 'anonymous':
                    if usr == 'anonymous':
                        perm = 'Anonymous'
                    else:
                        perm = 'Read-Only'
            # Complex roles (with more than one perm) are "Other"
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

        # First create a role for the desired permission
        role = permission.lower()
        try:
            nr.auth.addRole(role)
            nr.auth.addAcl(role, None, None, write=write, remove=remove)
            nr.auth.setAdmin(role, admin)
            nr.auth.setMirror(role, mirror)
        except errors.RoleAlreadyExists:
            # Not an error, but roll back the DB anyway
            nr.db.rollback()
        except:
            nr.db.rollback()
            raise

        # Now (maybe) create the user and add them to the role
        try:
            nr.auth.addUser(user, password)
            nr.auth.addRoleMember(role, user)
        except:
            nr.db.rollback()
            raise

        return True

    def deleteUser(self, schedId, execId, user):
        nr = self._getNetworkRepo()
        try:
            nr.auth.deleteUserByName(user)
        except:
            nr.db.rollback()
            raise

        return True

    def changePassword(self, schedId, execId, user, newPass):
        nr = self._getNetworkRepo()
        try:
            nr.auth.changePassword(user, newPass)
        except:
            nr.db.rollback()
            raise

        return True
