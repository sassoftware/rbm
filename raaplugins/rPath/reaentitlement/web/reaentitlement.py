# Copyright (c) 2006-2008 rPath, Inc
# All rights reserved

import sys
import raa.web
from raa.modules.raawebplugin import rAAWebPlugin
from raa.modules.raawebplugin import immedTask
from rPath.reaentitlement.web import migrateSpecialUseTableToProperties
import cherrypy

from raa.db.database import DatabaseTable, writeOp, readOp
from raa.db.data import RDT_STRING
from raa.localhostonly import localhostOnly

import traceback
import logging
log = logging.getLogger('rPath.reaentitlement')

ENTITLEMENT_KEY = "Entitlement Key"

class rEAEntitlement(rAAWebPlugin):
    '''
        This plugin configures an rEA entitlement.
    '''

    displayName = _("Manage Administrative Entitlement")

    cnrPath = "/srv/conary/repository.cnr"

    def initPlugin(self):
        migrateSpecialUseTableToProperties(self, self.pluginProperties.db,
            'plugin_rpath_rEAEntitlementTable', ['ent_key'], [ENTITLEMENT_KEY])

    def _getReposCfg(self):
        # Get repository hostnames and fqdn
        from conary.repository.netrepos.netserver import ServerConfig
        import os
        cfg = ServerConfig()
        cfg.read(self.cnrPath)
        serverNames = cfg.serverName
        hostName = os.uname()[1]
        return serverNames, hostName

    @raa.web.expose(html="rPath.reaentitlement.reaentitlement")
    def index(self):
        serverNames, hostName = self._getReposCfg()
        return dict(key=self.getPropertyValue(ENTITLEMENT_KEY),
            serverNames = serverNames, hostName = hostName)

    @raa.web.expose(html="rPath.reaentitlement.reaentitlement")
    def setkey(self, key=''):
        try:
            if self.callBackend('setkey', key):
                self.setPropertyValue(ENTITLEMENT_KEY, key)
        except Exception, e:
            log.error(traceback.format_exc(sys.exc_info()[2]))
            return dict(errors = [str(e)])

        
        serverNames, hostName = self._getReposCfg()
        return dict(key=self.getPropertyValue(ENTITLEMENT_KEY),
            serverNames = serverNames, hostName = hostName)

