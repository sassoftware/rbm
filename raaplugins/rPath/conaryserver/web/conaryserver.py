# Copyright (c) 2006 rPath, Inc
# All rights reserved

from raa.modules.raawebplugin import rAAWebPlugin
from raa.modules.raawebplugin import immedTask
import turbogears
import cherrypy
import raa

from reposconary.conary.repository.netrepos.netserver import ServerConfig
from reposconary.conary.lib.cfgtypes import CfgEnvironmentError
from reposconary.conary import dbstore
from raa.db.database import DatabaseTable, writeOp, readOp
from raa.localhostonly import localhostOnly
from reposconary.conary.repository.netrepos import netauth

class SrvChangeTable(DatabaseTable):
    name = 'plugin_rpath_SrvChangeTable'
    createSQL = """CREATE TABLE %s
                   (srvname VARCHAR(255))""" % (name)
    fields = ['srvname']
    tableVersion = 1

    @writeOp
    def clearserver(self, cu, srvname):
        self.db.transaction()
        cu.execute("DELETE FROM %s WHERE srvname=?" % (self.name), srvname)
        return True

    @writeOp
    def setserver(self, cu, srvname):
        self.db.transaction()
        # Check the table is empty.
        cu.execute("SELECT COUNT(*) FROM %s WHERE srvname=?" % (self.name),
                   srvname)
        if not cu.fetchone()[0]:
            cu.execute("INSERT INTO %s (srvname) VALUES (?)" % \
                       (self.name), srvname)
            return True
        return False

    @readOp
    def getdata(self, cu):
        cu.execute("""SELECT srvname FROM %s""" % (self.name))
        return [x[0] for x in cu.fetchall()]

    @readOp
    def countEntries(self, cu):
        cu.execute("SELECT COUNT(*) FROM %s" % self.name)
        return cu.fetchone()[0]

class ConaryServer(rAAWebPlugin):
    '''
        This plugin configures the conary repository hostnames.
    '''

    displayName = _("Update Repository Hostnames")

    tableClass = SrvChangeTable

    roles = ['mirror']

    cnrPath = '/srv/conary/repository.cnr'

    @turbogears.expose(html="rPath.conaryserver.config")
    @turbogears.identity.require( turbogears.identity.not_anonymous() )
    def index(self):
        try:
            cfg = ServerConfig()
            cfg.read(self.cnrPath)
            data = cfg.serverName
        except CfgEnvironmentError:
            pageText="""rPath Appliance Platform Update Server could
                        not read the configuration file "%s".  Please ensure
                        Update Server is properly installed.""" % self.cnrPath
            errorState = 'error'
        else:
            pageText = """<p>NOTE: In normal operation, you should not have to
                          make any changes using this interface.  The outbound
                          mirror configuration process will communicate the
                          necessary information to Update Server, which will
                          automatically configure itself.</p>

                          <p>This interface is provided for support purposes
                          only.</p>"""
            errorState = 'guide'
        
        return dict(data=[(x, self.checkRepository(cfg, x)) for x in self.table.getdata()], 
                    pageText=pageText, errorState=errorState)

    # this is strange-looking, but it triggers the doTask on the backend anyway
    @immedTask
    def _update(self):
        return dict()

    @turbogears.expose(html="rPath.conaryserver.config",
                       allow_json=True)
    @turbogears.identity.require( turbogears.identity.not_anonymous() )
    def refreshConaryrc(self):
        self._update()
        return self.index()

    @turbogears.expose(html="rPath.conaryserver.config",
                       allow_json=True)
    @turbogears.identity.require( turbogears.identity.not_anonymous() )
    def setsrvname(self, srvname=''):
        try:
            cfg = ServerConfig()
            cfg.read(self.cnrPath)
        except CfgEnvironmentError:
            return self.index()

        if not srvname:
            pageText = "Blank hostname entered."
            errorState = 'error'
        else:
            self.table.setserver(srvname)
            self._update()

            # Reload the conary.cnr file to see if the update worked
            try:
                cfg = ServerConfig()
                cfg.read(self.cnrPath)
            except CfgEnvironmentError:
                return self.index()
            if srvname.strip() not in cfg.serverName:
                pageText = "Error:  Unable to update hostname."
                self.table.clearserver(srvname)
                errorState = 'error'
            else:
                pageText = "Repository name updated."
                errorState = 'success'

        return dict(pageText=pageText, 
                    data=[(x, self.checkRepository(cfg, x)) for x in self.table.getdata()], 
                    errorState=errorState)

    @turbogears.expose(html="rPath.conaryserver.config",
                       allow_json=True)
    @turbogears.identity.require( turbogears.identity.not_anonymous() )
    def delsrvname(self, srvname):
        try:
            cfg = ServerConfig()
            cfg.read(self.cnrPath)
        except CfgEnvironmentError:
            return self.index()

        if not self.checkRepository(cfg, srvname):
            errorState = 'error'
            pageText = "Unable to delete repository name because it is " \
                       "in use."
        else:
            self.table.clearserver(srvname)
            self._update()
            errorState='success'
            pageText = 'Repository name "%s" deleted.' % srvname

        return dict(pageText=pageText, 
                    data=[(x, self.checkRepository(cfg, x)) for x in self.table.getdata()],
                    errorState=errorState)

    def checkRepository(self, cfg, srvname):
        db = dbstore.connect(cfg.repositoryDB[1], cfg.repositoryDB[0])
        cu = db.cursor()
        subStr = '%/' + srvname + '@%'
        cu.execute("""SELECT * FROM Versions
                          LEFT JOIN Instances
                          ON Versions.versionId=Instances.versionId
                          WHERE version LIKE ? LIMIT 1""", subStr)
        res = not cu.fetchall()
        db.close()
        return res

    @cherrypy.expose()
    @localhostOnly()
    def getData(self):
        return self.table.getdata()

    @raa.expose(allow_xmlrpc=True)
    @raa.web.require(turbogears.identity.has_any_permission('mirror', 'admin'))
    def addServerName(self, servernames):
        try:
            cfg = ServerConfig()
            cfg.read(self.cnrPath)
        except CfgEnvironmentError:
            return False
        if type(servernames) != list:
            servernames = [servernames]

        serverNames = self.table.getdata()
        if set(servernames).issubset(set(serverNames)):
            return True
        else:
            for x in set(servernames).difference(set(serverNames)):
                self.table.setserver(x)
            self._update()
            try:
                cfg = ServerConfig()
                cfg.read(self.cnrPath)
            except CfgEnvironmentError:
                return False
            if not set(servernames).issubset(set(cfg.serverName)):
                return False
            else:
                return True

    @raa.expose(allow_xmlrpc=True)
    def delServerName(self, servername):
        try:
            cfg = ServerConfig()
            cfg.read(self.cnrPath)
        except CfgEnvironmentError:
            return False

        serverNames = self.table.getdata()
        if servername in serverNames:
            if not self.checkRepository(cfg, servername):
                return True
        self.table.clearserver(servername)
        self._update()
        try:
            cfg.read(self.cnrPath)
        except CfgEnvironmentError:
            return False
        if servername in cfg.serverName:
            return False
        else:
            return True
