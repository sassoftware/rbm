#
# Copyright (C) 2006 rPath, Inc.
# All rights reserved.
#
import cherrypy
import raatest

import rPath
from rPath.mirrorusers.web.mirrorusers import MirrorTable

from tests import webPluginTest
raaFramework = webPluginTest()
raaFramework.pseudoroot = cherrypy.root.mirrorusers.MirrorUsers


# XXX: not used yet, rAA freaks out when I substitute this for the new table object
class OldMirrorTable(MirrorTable):
    name = 'plugin_rpath_MirrorTable'
    createSQL = """CREATE TABLE %s (
        user VARCHAR(255),
        permission VARCHAR(255),
        password VARCHAR(255),
        operation VARCHAR(255))""" % (name)
    fields = ['schedId', 'user', 'permission', 'password', 'operation']
    tableVersion = 1


class MirrorUsersTest(raatest.rAATest):
    def setUp(self):
        raatest.rAATest.setUp(self)
        self.table = cherrypy.root.mirrorusers.MirrorUsers.table
        self.table.clear()

    def test_setdata(self):
        self.table.setdata(0, 'testuser', 'permission', 'password', 'test')

        assert self.table.getdata(0) == \
            [{'operation': 'test', 'password': 'password', 'user': 'testuser', 'permission': 'permission'}]

    def test_indexTitle(self):
        oldGetUserList = raaFramework.pseudoroot._getUserList
        raaFramework.pseudoroot._getUserList = lambda *args: 0
        self.table.setdata(0, 'existinguser', 'permission', '', '')
        self.requestWithIdent("/mirrorusers/MirrorUsers/")
        assert "<title>manage repository users</title>" in cherrypy.response.body[0].lower()
        raaFramework.pseudoroot._getUserList = oldGetUserList

    def test_addUser(self):
        # test for prompt
        result = self.callWithIdent(raaFramework.pseudoroot.add)
        assert result['message'].startswith('Enter the following information') and \
            result['error'] == False

        # test for mismatched passwords
        result = self.callWithIdent(raaFramework.pseudoroot.add,
            username = 'newuser', passwd1 = 'pass', passwd2 = 'notmatch')
        assert result == {'message': 'Passwords do not match. Please try again.', 'error': True}

        # test for blank username
        result = self.callWithIdent(raaFramework.pseudoroot.add,
            username = '', passwd1 = 'pass', passwd2 = 'pass')
        assert result == {'message': 'Please enter a user uame.', 'error': True}

        # test for blank username
        result = self.callWithIdent(raaFramework.pseudoroot.add,
            username = 'anonymous', passwd1 = 'pass', passwd2 = 'pass',
            perm = 'not anonymous')
        assert result == {'message': 'The user name "anonymous" is reserved.  '
            'Please choose a different user name.', 'error': True}

        # test for duplicate user
        oldGetUserList = raaFramework.pseudoroot._getUserList
        raaFramework.pseudoroot._getUserList = lambda *args: 0
        self.table.setdata(0, 'existinguser', '', '', '')
        result = self.callWithIdent(raaFramework.pseudoroot.add,
            username = 'existinguser', passwd1 = 'pass', passwd2 = 'pass')
        assert result == {'message': 'User "existinguser" already exists. '
            ' Please choose a different user name.', 'error': True}
        raaFramework.pseudoroot._getUserList = oldGetUserList
        self.table.clear()

        # test for success
        result = self.callWithIdent(raaFramework.pseudoroot.add,
            username = 'newuser', passwd1 = 'pass', passwd2 = 'pass')
        assert result == {'message': 'User "newuser" added with Anonymous permission.', 'error': False}

    def test_deleteUser(self):
        result = self.callWithIdent(raaFramework.pseudoroot.deleteUser,
            username = 'newuser')
        assert result == {'username': 'newuser'}

        result = self.callWithIdent(raaFramework.pseudoroot.deleteUser,
            username = 'newuser', confirm = True)
        assert result == {'userList': [], 'userData': []}

    def test_changePassword(self):
        result = self.callWithIdent(raaFramework.pseudoroot.changePassword,
            username = 'thisDoesntMatter', passwd1 = 'neitherDoesThis!',
            passwd2 = 'neitherDoesThis!')
        assert result == {'userList': [], 'userData': []}

        result = self.callWithIdent(raaFramework.pseudoroot.changePassword,
            username = 'thisDoesntMatter', passwd1 = 'neitherDoesThis!',
            passwd2 = 'doesntmatch!')
        assert result == {'username': 'thisDoesntMatter',
            'message': 'Passwords do not match. Please try again.', 'error': True}

        result = self.callWithIdent(raaFramework.pseudoroot.changePassword,
            username = 'thisDoesntMatter', passwd1 = '', passwd2 = '')
        assert result == {'username': 'thisDoesntMatter',
            'message': 'Enter a new password for the repository user "thisDoesntMatter":',
            'error': False}
