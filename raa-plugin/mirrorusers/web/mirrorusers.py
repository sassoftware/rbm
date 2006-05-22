# Copyright (c) 2006 rPath, Inc
# All rights reserved

from raa.db.schedule import ScheduleImmed
from raa.modules.raawebplugin import rAAWebPlugin
from raa.modules.raawebplugin import immedTask
import turbogears
import cherrypy

from raa.db.database import DatabaseTable, writeOp, readOp
from raa.localhostonly import localhostOnly

class MirrorTable(DatabaseTable):
    name = 'plugin_rpath_MirrorTable'
    createSQL = """CREATE TABLE %s 
                   (user VARCHAR(255),
                    permission VARCHAR(255),
                    password VARCHAR(255),
                    operation VARCHAR(255))""" % (name)
    fields = ['user', 'permission', 'password', 'operation']
    tableVersion = 1

    @writeOp
    def setdata(self, cu, user='', permission='', password='', operation=''):
        self.db.transaction()
        cu.execute("""INSERT INTO %s (user, permission, password, operation) 
                          VALUES (?, ?, ?, ?)""" % (self.name), user, 
                                                    permission,
                                                    password, operation)
        return True

    @readOp
    def getdata(self,cu):
        cu.execute("""SELECT user, permission, password, 
                      operation FROM %s""" % (self.name))
        return cu.fetchall_dict()

    @writeOp
    def cleardata(self, cu):
        self.db.transaction()
        cu.execute("DELETE FROM %s" % (self.name))
        return True

    @readOp
    def checkdata(self, cu):
        cu.execute("SELECT COUNT(*) FROM %s" % self.name)
        results = cu.fetchone()
        return not results[0]

class MirrorUsers(rAAWebPlugin):
    ''' 
    '''
    displayName = _("Manage Users")

    tableClass = MirrorTable

    @turbogears.expose(html="rPath.mirrorusers.users")
    @turbogears.identity.require( turbogears.identity.not_anonymous() )
    def index(self):
        self.table.cleardata()
        self.table.setdata(operation='list')
        schedId = self.schedule(ScheduleImmed())
        self.triggerImmed(schedId)
        userList = self.table.getdata()
        self.table.cleardata()
        userData = []

        displayClass = 0
        for x in userList:
            userData.append([x['user'], x['permission'],
                            displayClass and 'odd' or 'even'])
            displayClass = displayClass ^ 1
        return dict(userData=userData, userList=userList)

    @turbogears.expose(html="rPath.mirrorusers.add")
    @turbogears.identity.require( turbogears.identity.not_anonymous() )
    def add(self, username=None, passwd1=None, passwd2=None, perm='Anonymous'):
        if not username and not passwd1 and not passwd2:
            returnMessage='Add a new user.  Mirroring permission allows the user to mirror to this repository from an rBuilder instance.'
            errorState = False
        elif not username:
            returnMessage = "Please enter a User Name."
            errorState = True
        elif passwd1 != passwd2 or not passwd1:
            returnMessage = "Passwords do not match. Please try again."
            errorState = True
        elif username == 'anonymous' and perm != 'Anonymous':
            returnMessage = 'The User Name "anonymous" is reserved.  Please choose a different name.'
            errorState = True
        else:
            # Check to see if the user exists
            self.table.cleardata()
            self.table.setdata(operation='list')
            schedId = self.schedule(ScheduleImmed())
            self.triggerImmed(schedId)
            userList = self.table.getdata()
            self.table.cleardata()
            errorState = False
            for x in userList:
                if x['user'] == username:
                    returnMessage = 'User "%s" already exists.  Please choose a different name.' % username
                    errorState = True
            # Create the user
            if not errorState:
                self.table.setdata(user=username, password=passwd1,
                                   permission=perm, operation='add')
                schedId = self.schedule(ScheduleImmed())
                self.triggerImmed(schedId)
                returnMessage= 'User "%s" added with %s privileges.' % \
                             (username, perm)
        return dict(message=_(returnMessage), error=errorState)

    @turbogears.expose(html='rPath.mirrorusers.delete')
    @turbogears.identity.require( turbogears.identity.not_anonymous() )
    def deleteUser(self, username, confirm=False):
        if not confirm:
            return dict(username=username)
        else:
            self.table.setdata(user=username, operation='delete')
            schedId = self.schedule(ScheduleImmed())
            self.triggerImmed(schedId)
            return self.index()

    @turbogears.expose(html='rPath.mirrorusers.pass')
    @turbogears.identity.require( turbogears.identity.not_anonymous() )
    def changePassword(self, username, passwd1='', passwd2=''):
        if not passwd1:
            errorState=False
            message = 'Enter a new password for the conary user "%s":'\
                                                               % username
        elif passwd1 != passwd2: 
            message = "Passwords do not match. Please try again."
            errorState = True
        else:
            self.table.setdata(user=username, password=passwd1, 
                               operation='pass')
            schedId = self.schedule(ScheduleImmed())
            self.triggerImmed(schedId)
            return self.index()

        return dict(username=username, error=errorState, message=message)

    @cherrypy.expose
    @localhostOnly
    def getData(self):
        return self.table.getdata()

    @cherrypy.expose()
    @localhostOnly
    def setData(self, user, permission):
        return self.table.setdata(user=user, permission=permission)

    @cherrypy.expose
    @localhostOnly
    def clearData(self):
        return self.table.cleardata()
