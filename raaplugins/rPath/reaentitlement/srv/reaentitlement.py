#
# Copyright (C) 2006-2008, rPath, Inc.
# All rights reserved.
#

import random
from raa.modules.raasrvplugin import rAASrvPlugin
from conary.repository.netrepos.netserver import ServerConfig
from conary.repository.netrepos.netserver import NetworkRepositoryServer
from conary.repository.errors import UnknownEntitlementClass, RoleNotFound

import traceback
import sys
import logging
log = logging.getLogger("rPath.reaentitlement")

class rEAEntitlement(rAASrvPlugin):
    """
    Configure rEA entitlement.
    """

    reposserver = 'localhost'
    cnrPath ='/srv/conary/repository.cnr'

    def _genString(self):
        allowed = "abcdefghijklmnopqrstuvwxyz0123456789"
        len = 128
        passwd = ''
        for x in range(len):
            passwd += random.choice(allowed)
        return passwd

    def setkey(self, schedId, execId, key):
        entClass = 'management'
        entRole = 'management'

        cfg = ServerConfig()
        cfg.read(self.cnrPath)
        nr = NetworkRepositoryServer(cfg, self.reposserver)

        adminUser = self._genString()
        passwd = self._genString()
        authToken = [adminUser, passwd, None, None]

        try:
            nr.auth.addUser(adminUser, passwd)
            nr.auth.addAcl(adminUser, None, None, write=True)
            nr.auth.setAdmin(adminUser, True)

            # remove the old entitlement group if it exists
            try:
                nr.auth.deleteEntitlementClass(authToken, entRole)
            except UnknownEntitlementClass, e:
                pass

            # remove the old group if it exists
            try:
                nr.auth.deleteRole(entRole)
            except RoleNotFound, e:
                pass

            # add the management group and give it the proper ACLs
            nr.auth.addRole(entRole)
            nr.auth.addAcl(entRole, None, None, write=True)
            nr.auth.setAdmin(entRole, True)
            nr.auth.addEntitlementClass(authToken, entClass, entRole)
            nr.auth.addEntitlementKey(authToken, entClass, key)

        finally:
            nr.auth.deleteUserByName(adminUser)
        return True
