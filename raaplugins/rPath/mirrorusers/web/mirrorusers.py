#
# Copyright (c) SAS Institute Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import random

import raa.web
from raa.modules.raawebplugin import rAAWebPlugin
import raa.authorization
from gettext import gettext as _


class MirrorUsers(rAAWebPlugin):
    '''
    Create or delete conary repository users
    '''
    displayName = _("Manage Repository Users")

    roles = ['mirror']
    
    def initPlugin(self):
        if 'plugin_rpath_MirrorTable' in self.pluginProperties.db.tables:
            cu = self.pluginProperties.db.cursor()
            cu.execute("DROP TABLE plugin_rpath_MirrorTable")
            self.pluginProperties.db.commit()

    def _getUserList(self):
        return self.callBackend('getUserList')

    @raa.web.expose(template="rPath.mirrorusers.templates.users")
    def index(self, *args, **kwargs):
        userList = self._getUserList()
        userData = []
        displayClass = 0
        for x in userList:
            userData.append([x['user'], x['permission'],
                            displayClass and 'odd' or 'even'])
            displayClass = displayClass ^ 1
        return dict(userData=userData, userList=userList)

    def _addUser(self, username, password, permission):
        return self.callBackend('addUser', username, password, permission)

    @raa.web.expose(template="rPath.mirrorusers.templates.add")
    def add(self, username=None, passwd1=None, passwd2=None, perm='Anonymous'):
        returnMessage="""Enter the following information, select the 
                         desired permission, and click on the "Apply" 
                         button to create a repository user."""
        if not username and not passwd1 and not passwd2:
            errorState = False
        elif not username:
            errorMessage = "Please enter a user name."
            errorState = True
        elif passwd1 != passwd2 or not passwd1:
            errorMessage = "Passwords do not match. Please try again."
            errorState = True
        elif username == 'anonymous' and perm != 'Anonymous':
            errorMessage = 'The user name "anonymous" is reserved.  Please choose a different user name.'
            errorState = True
        else:
            result = self._addUser(username, passwd1, perm)
            if 'error' in result:
                errorState = True
                if result['error'] == 'UserAlreadyExists':
                    errorMessage = ('User "%s" already exists.  Please choose '
                        'a different user name.' % username)
                elif result['error'] == 'InvalidName':
                    errorMessage = ('The user name "%s" is invalid.  Please '
                        'choose a different user name.' % username)
                else:
                    errorMessage = result['error']
            else:
                errorState = False
                returnMessage = 'User "%s" added with %s permission.' % \
                         (username, perm)

        if errorState:
            return dict(errors=_(errorMessage), message=_(returnMessage), error=True)
        else:
            return dict(message=_(returnMessage), error=False)

    def _deleteUser(self, username):
        return self.callBackend('deleteUser', username)

    @raa.web.expose(allow_json=True)
    def deleteUser(self, username):
        try:
            self._deleteUser(username)
        except Exception, e:
            return(dict(errors=[ repr(e) ]))
        return dict(message="User %s has been deleted from the repository." % username)

    def _changePassword(self, username, password):
        return self.callBackend('changePassword', username, password)

    @raa.web.expose(allow_json=True)
    @raa.web.reauthorize
    def changePassword(self, username, pwd1, pwd2):
        if not pwd1:
            errors = 'Enter a new password for the repository user "%s":'\
                                                               % username
        elif pwd1 != pwd2: 
            errors = "Passwords do not match. Please try again."
        else:
            return self._changePassword(username, pwd1)

        return dict(errors=errors, message=message)

    def _genString(self):
        allowed = "abcdefghijklmnopqrstuvwxyz0123456789"
        len = 128
        chars = ''
        for x in range(len):
            chars += random.choice(allowed)
        return chars

    @raa.web.expose(allow_xmlrpc=True)
    @raa.web.require(raa.authorization.PermissionPresent('mirror'))
    def addRandomUser(self, user):
        passwd = self._genString()
        result = self._addUser(user, passwd, 'Mirror')
        error = result.get('error')
        if error:
            if error == 'UserAlreadyExists':
                pass
            elif error == 'ProxyMode':
                return ''
            else:
                raise RuntimeError(error)
        else:
            return passwd
        # User exists, but the password is gone, so just delete it
        # and recreate (and return the new password as usual).
        self._deleteUser(user)
        result = self._addUser(user, passwd, 'Mirror')
        if 'error' in result:
            raise RuntimeError(result['error'])
        return passwd

    @raa.web.expose(allow_xmlrpc=True)
    def deleteRandomUser(self, username):
        self._deleteUser(username)
        return True
