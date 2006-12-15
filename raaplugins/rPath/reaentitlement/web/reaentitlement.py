# Copyright (c) 2006 rPath, Inc
# All rights reserved

from raa.db.schedule import ScheduleImmed
from raa.modules.raawebplugin import rAAWebPlugin
from raa.modules.raawebplugin import immedTask
import turbogears
import cherrypy

from conary import dbstore
from raa.db.database import DatabaseTable, writeOp, readOp
from raa.localhostonly import localhostOnly

class KeyChangeTable(DatabaseTable):
    name = 'plugin_rpath_rEAEntitlementTable'
    createSQL = """CREATE TABLE %s
                   (ent_key VARCHAR(255))""" % (name)
    fields = ['ent_key']
    tableVersion = 1

    @writeOp
    def setkey(self, cu, key):
        self.db.transaction()
        cu.execute("DELETE FROM %s" % self.name)
        cu.execute("INSERT INTO %s (ent_key) VALUES (?)" % self.name, key)
        return True

    @readOp
    def getkey(self, cu):
        cu.execute("""SELECT ent_key FROM %s""" % (self.name))
        key = cu.fetchone()
        if not key:
            return ''
        else:
            return key[0]

class rEAEntitlement(rAAWebPlugin):
    '''
        This plugin configures an rEA entitlement.
    '''

    displayName = _("Manage Administrative Entitlement")

    tableClass = KeyChangeTable
    cnrPath = "/srv/conary/repository.cnr"

    def _getReposCfg(self):
        # Get server names and hostname
        from conary.repository.netrepos.netserver import ServerConfig
        import os
        cfg = ServerConfig()
        cfg.read(self.cnrPath)
        serverNames = cfg.serverName
        hostName = os.uname()[1]
        return serverNames, hostName

    @turbogears.expose(html="rPath.reaentitlement.reaentitlement")
    @turbogears.identity.require( turbogears.identity.not_anonymous() )
    def index(self):
        serverNames, hostName = self._getReposCfg()
        return dict(key=self.table.getkey(),
            serverNames = serverNames, hostName = hostName)

    @immedTask
    def _setkey(self, key):
        def callback(schedId):
            self.table.setkey(key)
        return dict(callback = callback)

    @turbogears.expose(html="rPath.reaentitlement.reaentitlement",
                       allow_json=True)
    @turbogears.identity.require( turbogears.identity.not_anonymous() )
    def setkey(self, key=''):
        self._setkey(key)
        
        serverNames, hostName = self._getReposCfg()
        return dict(key=self.table.getkey(),
            serverNames = serverNames, hostName = hostName)

    @cherrypy.expose()
    @localhostOnly()
    def getKey(self):
        return self.table.getkey()
