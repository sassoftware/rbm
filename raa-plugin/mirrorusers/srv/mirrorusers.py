#
# Copyright (c) 2005-2006 rPath, Inc.
#
# All rights reserved
#

from raa.modules.raasrvplugin import rAASrvPlugin
from conary.repository.netrepos.netserver import ServerConfig
from conary.repository.netrepos.netserver import NetworkRepositoryServer
from conary.lib.cfgtypes import CfgEnvironmentError
from conary.repository import errors

class MirrorUsers(rAASrvPlugin):
    def doTask(self, schedId, execId):
        '''
            Lists, adds, deletes, or changes password
            for a conary user.
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
                perm = 'Other'
                for x in nr.auth.userAuth.getGroupsByUser(usr):
                    # anonymous user
                    if x == 'anonymous':
                        perm = 'Anonymous'
                        break
                    perms = nr.auth.iterPermsByGroup(x)
                    for i in perms:
                        # admin user
                        if i == ('ALL', 'ALL', 1, 0, 1, 0):
                            perm = 'Admin'
                            break
                        # mirror user
                        elif nr.auth.groupCanMirror(x) and \
                                i == ('ALL', 'ALL', 1, 0, 0, 0):
                            perm = 'Mirroring'
                            break
                self.server.setData(usr, perm)
        elif data[0]['operation'] == 'add':
            if data[0]['permission'] == 'Mirror':
                write = True
                mirror = True
                admin = False
            elif data[0]['permission'] == 'Anonymous':
                write = False
                mirror = False
                admin = False
            elif data[0]['permission'] == 'Admin':
                write = True
                mirror = False
                admin = True
            try:
                nr.auth.addUser(data[0]['user'], data[0]['password'])
                nr.auth.addAcl(data[0]['user'], None, None, write,
                               False, admin)
                nr.auth.setMirror(data[0]['user'], mirror)
            except errors.GroupAlreadyExists:
                pass
        elif data[0]['operation'] == 'delete':
            nr.auth.deleteUserByName(data[0]['user'])
        elif data[0]['operation'] == 'pass':
            nr.auth.changePassword(data[0]['user'], data[0]['password'])
