# Copyright (c) 2006 rPath, Inc
# All rights reserved

from raa.db.schedule import ScheduleImmed
from raa.modules.raawebplugin import rAAWebPlugin
import turbogears
import cherrypy

from conary.repository.netrepos.netserver import ServerConfig
from conary.lib.cfgtypes import CfgEnvironmentError
from conary import dbstore
from raa.db.database import DatabaseTable, writeOp, readOp
from raa.localhostonly import localhostOnly

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

    displayName = _("Conary Repository Server")
    tooltip = _("Update the server name of your Conary repository")

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
            pageText="""rPath Conary Repository Appliance could not
                        be located.  Please ensure that it is
                        properly installed."""
            errorState = 'error'
        else:
            pageText = """Use this page to update the hostnames of your Conary
                          repository. Note that once any changes have been
                          committed to the repository using a specific hostname,
                          it will not be possible to delete that hostname."""
            errorState = 'guide'
        
        return dict(data=[(x, self.checkRepository(cfg, x)) for x in self.table.getdata()], 
                    pageText=pageText, errorState=errorState)

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
            pageText = "Error:  Blank hostname entered."
            errorState = 'error'
        else:
            self.table.setserver(srvname)
            schedId = self.schedule(ScheduleImmed())
            self.triggerImmed(schedId)

            # Reload the conary.cnr file to see if the update worked
            try:
                cfg = ServerConfig()
                cfg.read(self.cnrPath)
            except CfgEnvironmentError:
                return self.index()
            if srvname.strip() not in cfg.serverName:
                pageText = "Error:  Unable to update hostname."
                errorState = 'error'
            else:
                pageText = "Conary repository hostname updated."
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
            pageText = "Unable to delete repository hostname because it is " \
                       "in use"
        else:
            self.table.clearserver(srvname)
            schedId = self.schedule(ScheduleImmed())
            self.triggerImmed(schedId)
            errorState='success'
            pageText = '%s deleted.' % srvname

        return dict(pageText=pageText, 
                    data=[(x, self.checkRepository(cfg, x)) for x in self.table.getdata()], 
                    errorState=errorState)
        
    def checkRepository(self, cfg, srvname):
        if self.table.countEntries() < 2:
            return False
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

    @cherrypy.expose
    @localhostOnly
    def getData(self):
        return self.table.getdata()
