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
                   (schedId VARCHAR(255),
                    user VARCHAR(255),
                    permission VARCHAR(255),
                    password VARCHAR(255),
                    operation VARCHAR(255))""" % (name)
    fields = ['schedId', 'user', 'permission', 'password', 'operation']
    tableVersion = 2

    @writeOp
    def setdata(self, cu, schedId, user='', permission='', password='', 
                operation=''):
        self.db.transaction()
        cu.execute("""INSERT INTO %s (schedId, user, permission, password, 
                      operation) VALUES (?, ?, ?, ?, ?)""" % (self.name), schedId, user, 
                                                          permission,
                                                          password, operation)
        return True

    @readOp
    def getdata(self,cu, schedId):
        cu.execute("""SELECT user, permission, password, 
                      operation FROM %s WHERE schedId=?""" % (self.name),
                                                               schedId)
        return cu.fetchall_dict()

    def versionCheck(self, cu):
        if self.getVersion(cu) == 1:
            cu.execute("DELETE FROM %s" % (self.name))
            cu.execute("ALTER TABLE %s ADD COLUMN schedId VARCHAR(255)" % self.name)
            return False
        return True

class MirrorUsers(rAAWebPlugin):
    ''' 
    '''
    displayName = _("Manage Repository Users")

    tableClass = MirrorTable

    @turbogears.expose(html="rPath.mirrorusers.users")
    @turbogears.identity.require( turbogears.identity.not_anonymous() )
    @immedTask
    def index(self, *args, **kwargs):
        schedId = self.schedule(ScheduleImmed())
        self.table.setdata(schedId=str(schedId), operation='list')
        userList = self.table.getdata(schedId)
        userList = [x for x in userList if x['user'] and x['permission']]
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
            returnMessage="""Enter the following information, select the 
                             desired permission, and click on the "Apply" 
                             button to create a repository user."""
            errorState = False
        elif not username:
            returnMessage = "Please enter a user uame."
            errorState = True
        elif passwd1 != passwd2 or not passwd1:
            returnMessage = "Passwords do not match. Please try again."
            errorState = True
        elif username == 'anonymous' and perm != 'Anonymous':
            returnMessage = 'The user name "anonymous" is reserved.  Please choose a different user name.'
            errorState = True
        else:
            # Check to see if the user exists
            schedId = self.schedule(ScheduleImmed())
            self.table.setdata(schedId=schedId, operation='list')
            self.triggerImmed(schedId)
            userList = self.table.getdata(schedId)
            errorState = False
            for x in userList:
                if x['user'] == username:
                    returnMessage = 'User "%s" already exists.  Please choose a different user name.' % username
                    errorState = True
            # Create the user
            if not errorState:
                schedId = self.schedule(ScheduleImmed())
                self.table.setdata(schedId=schedId, user=username, 
                                   password=passwd1,
                                   permission=perm, operation='add')
                self.triggerImmed(schedId)
                returnMessage= 'User "%s" added with %s permission.' % \
                             (username, perm)
        return dict(message=_(returnMessage), error=errorState)

    @turbogears.expose(html='rPath.mirrorusers.delete')
    @turbogears.identity.require( turbogears.identity.not_anonymous() )
    def deleteUser(self, username, confirm=False):
        if not confirm:
            return dict(username=username)
        else:
            schedId = self.schedule(ScheduleImmed())
            self.table.setdata(schedId=schedId, user=username, 
                               operation='delete')
            self.triggerImmed(schedId)
            return self.index()

    @turbogears.expose(html='rPath.mirrorusers.pass')
    @turbogears.identity.require( turbogears.identity.not_anonymous() )
    def changePassword(self, username, passwd1='', passwd2=''):
        if not passwd1:
            errorState=False
            message = 'Enter a new password for the repository user "%s":'\
                                                               % username
        elif passwd1 != passwd2: 
            message = "Passwords do not match. Please try again."
            errorState = True
        else:
            schedId = self.schedule(ScheduleImmed())
            self.table.setdata(schedId=schedId, user=username, 
                               password=passwd1, operation='pass')
            self.triggerImmed(schedId)
            return self.index()

        return dict(username=username, error=errorState, message=message)

    @cherrypy.expose()
    @localhostOnly()
    def getData(self, schedId):
        return self.table.getdata(schedId)

    @cherrypy.expose()
    @localhostOnly()
    def setData(self, schedId, user, permission):
        return self.table.setdata(schedId=schedId, user=user, permission=permission)
