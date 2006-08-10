#
# Copyright (C) 2006, rPath, Inc.
# All rights reserved.
#

import random
from raa.modules.raasrvplugin import rAASrvPlugin
from conary.repository.netrepos.netserver import ServerConfig
from conary.repository.netrepos.netserver import NetworkRepositoryServer
from conary.repository import errors

class rEAEntitlement(rAASrvPlugin):
    """
    Configure rEA entitlement.
    """

    def _genString(self):
        allowed = "abcdefghijklmnopqrstuvwxyz0123456789"
        len = 128
        passwd = ''
        for x in range(len):
            passwd += random.choice(allowed)
        return passwd

    def doTask(self, schedId, execId):
        entClass = 'management'
        entGroup = 'management'
        cnrPath ='/srv/conary/repository.cnr'
        key = self.server.getKey()

        cfg = ServerConfig()
        cfg.read(cnrPath)
        nr = NetworkRepositoryServer(cfg, 'localhost')

        adminUser = self._genString()
        passwd = self._genString()
        authToken = [adminUser, passwd, None, None]

        try:
            nr.auth.addUser(adminUser, passwd)
            nr.auth.addAcl(adminUser, None, None, True, False, True)

            try:
                nr.auth.addGroup(entGroup)
                nr.auth.addAcl(entGroup, None, None, True, False, True)
            except errors.GroupAlreadyExists:
                for x in nr.auth.iterEntitlements(authToken, entGroup):
                    nr.auth.deleteEntitlement(authToken, entGroup, x)
                nr.auth.addEntitlement(authToken, entClass, key)
            else:
                try:
                    nr.auth.addEntitlementGroup(authToken, entClass, entGroup)
                except errors.GroupAlreadyExists:
                    nr.auth.deleteEntitlementGroup(authToken, entGroup)
                    nr.auth.addEntitlementGroup(authToken, entClass, entGroup)
                    for x in nr.auth.iterEntitlements(authToken, entGroup):
                        nr.auth.deleteEntitlement(authToken, entGroup, x)
                nr.auth.addEntitlement(authToken, entClass, key)
        finally:
            nr.auth.deleteUserByName(adminUser)
