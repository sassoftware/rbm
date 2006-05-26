# Copyright (c) 2006 rPath, Inc
# All rights reserved

from raa.db.schedule import ScheduleImmed
from raa.db.rpath_error import ItemNotFound, DuplicateItem
from raa.modules.raawebplugin import rAAWebPlugin
from raa.modules.raawebplugin import immedTask
import turbogears
import cherrypy

from conary.repository.netrepos.netserver import ServerConfig
from conary.lib.cfgtypes import CfgEnvironmentError
from conary.repository import netclient
from conary import conarycfg
from conary import dbstore
from raa.db.database import DatabaseTable, writeOp, readOp
from raa.db.lumberjack import *
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
        This plugin configures the conary repository server name.
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
            return dict(data='unknown', 
                        pageText="""rPath Conary Repository Appliance could not
                                    be located.  Please ensure that it is 
                                    properly installed.
                                 """,
                        editable=False)

        normalText = """Use this page to update the hostname of your Conary 
                        repository. Note that once any changes have been 
                        committed to the repository, it will not be possible 
                        to change this value."""
        noEditText = """Changes have already been commited to the repository
                        hosted on:  %s\n
                        \n
                        Changing the hostname at this point is not
                        permitted.""" % data

        editable = self.checkRepository(cfg)
        if editable:
            pageText = normalText
        else:
            pageText = noEditText

        return dict(data=data, pageText=pageText, editable=editable)

    @turbogears.expose(html="rPath.conaryserver.complete",
                       allow_json=True)
    @turbogears.identity.require( turbogears.identity.not_anonymous() )
    def chsrvname(self, srvname=''):
        errorState = False

        try:
            cfg = ServerConfig()
            cfg.read(self.cnrPath)
        except CfgEnvironmentError:
            return self.index()

        # Revalidate that nothing has been committed
        if not self.checkRepository(cfg):
            return self.index()

        if not srvname:
            pageText = "Error:  Blank hostname entered."
            errorState = True
        else:
            self.table.setdata(srvname)
            schedId = self.schedule(ScheduleImmed())
            self.triggerImmed(schedId)
        
            # Reload the conary.cnr file to see if the update worked
            try:
                cfg = ServerConfig()
                cfg.read(self.cnrPath)
            except CfgEnvironmentError:
                return self.index()
            if cfg.serverName != srvname.strip(' '):
                pageText = "Error:  Unable to update hostname."
                errorState = True
            else:
                pageText = "Conary repository hostname updated."

        return dict(pageText=pageText, srvname=cfg.serverName, 
                    errorState=errorState)

    def checkRepository(self, cfg, srvname):
        if self.table.countEntries() < 2:
            return False
        db = dbstore.connect(cfg.repositoryDB[1], cfg.repositoryDB[0])
        cu = db.cursor()
        cu.execute("""SELECT EXISTS(
                          SELECT * FROM Versions
                          LEFT JOIN Instances
                              ON Versions.versionId=Instances.versionId
                          WHERE version LIKE '%/?@%' LIMIT 1);""", srvname)
        res = cu.fetchone()[0]
        db.close()
        return not res

    @cherrypy.expose
    @localhostOnly
    def getData(self):
        return self.table.getdata()
