# Copyright (c) 2006 rPath, Inc
# All rights reserved

from raa.db.schedule import ScheduleImmed
from raa.db.rpath_error import ItemNotFound, DuplicateItem
from raa.modules.raaplugin import rAAWebPlugin
from raa.modules.raaplugin import rAASrvPlugin
from raa.modules.raaplugin import immedTask
import turbogears
import cherrypy

from conary.repository.netrepos.netserver import ServerConfig
from conary.lib.cfgtypes import CfgEnvironmentError
from conary.repository import netclient
from conary import conarycfg
from conary import dbstore
from raa.db.database import DatabaseTable, writeOp, readOp
from raa.db.lumberjack import *

class SrvChangeTable(DatabaseTable):
    name = 'plugin_rpath_SrvChangeTable'
    createSQL = """CREATE TABLE %s 
                   (newsrv VARCHAR(255))""" % (name)
    fields = ['newsrv']

    @writeOp
    def setdata(self, cu, srvname):
        self.db.transaction()
        # Check the table is empty.
        cu.execute("SELECT COUNT(*) FROM %s" % (self.name))
        results = cu.fetchone()
        if results[0]:
            cu.execute("UPDATE %s SET newsrv=?" % (self.name), srvname)
            return True
        else:
            cu.execute("""INSERT INTO %s (newsrv) 
                          VALUES (?)""" % (self.name), srvname)
            return True

    @readOp
    def getdata(self,cu):
        cu.execute("""SELECT newsrv FROM %s""" % (self.name))
        results = cu.fetchall()
        if len(results) == 0:
            raise ItemNotFound('newsrv')
        if len(results) > 1:
            raise DuplicateItem('newsrv')
        return results[0]

class ConaryServer(rAAWebPlugin):
    '''
        This plugin configures the conary repository server name.
    '''

    displayName = _("Conary Repository Server")
    tooltip = _("Update the server name of your Conary repository")

    tableClass = SrvChangeTable
    
    cnrPath = '/srv/conary/repository.cnr'

    @turbogears.expose(html="raa.modules.conaryserver.config")
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

    @turbogears.expose(html="raa.modules.conaryserver.complete",
                       allow_json=True)
    @turbogears.identity.require( turbogears.identity.not_anonymous() )
    def chsrvname(self, newsrv=''):
        errorState = False

        try:
            cfg = ServerConfig()
            cfg.read(self.cnrPath)
        except CfgEnvironmentError:
            return self.index()

        # Revalidate that nothing has been committed
        if not self.checkRepository(cfg):
            return self.index()

        if not newsrv:
            pageText = "Error:  Blank hostname entered."
            errorState = True
        else:
            self.table.setdata(newsrv)
            self.schedule(ScheduleImmed())
            self.triggerImmed()
        
            # Reload the conary.cnr file to see if the update worked
            try:
                cfg = ServerConfig()
                cfg.read(self.cnrPath)
            except CfgEnvironmentError:
                return self.index()
            if cfg.serverName != newsrv.strip(' '):
                pageText = "Error:  Unable to update hostname."
                errorState = True
            else:
                pageText = "Conary repository hostname updated."

        return dict(pageText=pageText, srvname=cfg.serverName, 
                    errorState=errorState)

    def checkRepository(self, cfg):
        db = dbstore.connect(cfg.repositoryDB[1], cfg.repositoryDB[0])
        cu = db.cursor()
        cu.execute("SELECT COUNT(*) FROM Instances")
        res = cu.fetchone()[0]
        db.close()
        return not res

    @cherrypy.expose()
    def getData(self):
        return dict(self.table.getdata())

class SrvNameTask(rAASrvPlugin):
    def doTask(self, taskId, schedId, execId):
        '''
            Updates serverName in conaryCNR if no commits have occured in the
            repository.

        '''

        cnrPath = '/srv/conary/repository.cnr'

        data = self.server.getData()

        try:
            cfg = ServerConfig()
            cfg.read(cnrPath)
            cfg.serverName = data['newsrv']
        except CfgEnvironmentError:
            pass

        try:
            f = open(cnrPath, "w")
            cfg.display(f)
            f.close()
        except IOError:
            pass
