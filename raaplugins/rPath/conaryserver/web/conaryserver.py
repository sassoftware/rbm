# Copyright (c) 2006 rPath, Inc
# All rights reserved

from raa.modules.raawebplugin import rAAWebPlugin
from raa.modules.raawebplugin import immedTask
import turbogears
import cherrypy
import raa

from conary.repository.netrepos.netserver import ServerConfig
from conary.lib.cfgtypes import CfgEnvironmentError
from conary import dbstore
from raa.db.database import DatabaseTable, writeOp, readOp
from raa.localhostonly import localhostOnly
from conary.repository.netrepos import netauth

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
        This plugin configures the conary repository server names.
    '''

    displayName = _("Update Repository Server Names")

    tableClass = SrvChangeTable

    cnrPath = '/srv/conary/repository.cnr'

    @turbogears.expose(html="rPath.conaryserver.config")
    @turbogears.identity.require( turbogears.identity.not_anonymous() )
    def index(self):
        try:
            cfg = ServerConfig()
            cfg.read(self.cnrPath)
            data = cfg.serverName
        except CfgEnvironmentError:
            pageText="""rBuilder Mirror could not read the configuration 
                        file "%s".  Please ensure rBuilder Mirror is
                        properly installed.""" % self.cnrPath
            errorState = 'error'
        else:
            pageText = """<p>To use rBuilder Mirror, you must specify one or 
                          more server names reflecting the server name 
                          portion(s) of the label(s) you wish to mirror.</p>

                          <p>For example, given a repository containing software
                          under the <tt>repo.example.com@org:prod-1</tt> label,
                          the server name <tt>repo.example.com</tt> should be 
                          entered here.</p>

                          <p>Enter the desired server name, and click on the 
                          "Add" button.  Incorrectly-entered server names can 
                          be deleted by clicking on the corresponding [X] icon;
                          however, once software has been committed to the
                          repository under a given label, its server name may 
                          no longer be deleted.</p>

                          <p>NOTE: You <em>must</em> specify at least one 
                          server name here.</p>
                          <p>NOTE: httpd will automatically be restarted after
                          each new hostname is added or deleted (This is 
                          necessary for the server name changes to take effect).
                          This may cause a slight disruption to your service 
                          while the restart is in progress.</p>"""
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
    def addServerName(self, servername):
        try:
            cfg = ServerConfig()
            cfg.read(self.cnrPath)
        except CfgEnvironmentError:
            return False

        serverNames = self.table.getdata()
        if servername in serverNames:
            return True
        else:
            self.table.setserver(servername)
            self._update()
            try:
                cfg = ServerConfig()
                cfg.read(self.cnrPath)
            except CfgEnvironmentError:
                return False
            if servername not in cfg.serverName:
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
