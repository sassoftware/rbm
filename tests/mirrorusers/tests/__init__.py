#
# Copyright (C) 2006 rPath, Inc.
# All rights reserved.
#
import cherrypy
import raatest

import rPath
import re

from tests import webPluginTest
raaFramework = webPluginTest()
raaFramework.pseudoroot = cherrypy.root.mirrorusers.MirrorUsers


class MirrorUsersTest(raatest.rAATest):
    def setUp(self):
        #raatest.rAATest.setUp(self)
        self._getUserList = raaFramework.pseudoroot._getUserList
        self._addUser = raaFramework.pseudoroot._addUser
        self._deleteUser = raaFramework.pseudoroot._deleteUser
        self._changePassword = raaFramework.pseudoroot._changePassword

    def tearDown(self):
        raaFramework.pseudoroot._getUserList = self._getUserList 
        raaFramework.pseudoroot._addUser = self._addUser
        raaFramework.pseudoroot._deleteUser = self._deleteUser
        raaFramework.pseudoroot._changePassword = self._changePassword

    def test_indexTitle(self):
        raaFramework.pseudoroot._getUserList = lambda *args: [{'user': 'testguy', 'permission':'blah'}]
        self.requestWithIdent("/mirrorusers/MirrorUsers/")
        assert "<title>manage repository users</title>" in cherrypy.response.body[0].lower()

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
        raaFramework.pseudoroot._addUser = lambda *args: False
        result = self.callWithIdent(raaFramework.pseudoroot.add,
            username = 'existinguser', passwd1 = 'pass', passwd2 = 'pass')
        assert result == {'message': 'User "existinguser" already exists. '
            ' Please choose a different user name.', 'error': True}

        # test for success
        raaFramework.pseudoroot._addUser = lambda *args: True
        result = self.callWithIdent(raaFramework.pseudoroot.add,
            username = 'newuser', passwd1 = 'pass', passwd2 = 'pass')
        assert result == {'message': 'User "newuser" added with Anonymous permission.', 'error': False}

    def test_deleteUser(self):
        raaFramework.pseudoroot._deleteUser = lambda *args: True
        result = self.callWithIdent(raaFramework.pseudoroot.deleteUser, 'newuser')
        assert result == {'username': 'newuser'}

        raaFramework.pseudoroot._getUserList = lambda *args: []
        result = self.callWithIdent(raaFramework.pseudoroot.deleteUser,
            username = 'newuser', confirm = True)
        assert result == {'userList': [], 'userData': []}

    def test_changePassword(self):
        raaFramework.pseudoroot._getUserList = lambda *args: []
        raaFramework.pseudoroot._changePassword = lambda *args: True
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

    def test_addRandomness(self):
        raaFramework.pseudoroot._addUser = lambda *args: True
        raaFramework.pseudoroot._deleteUser = lambda *args: True
        r = self.callXmlrpc(raaFramework.pseudoroot.addRandomUser, 
                               'testuser')
        value = re.compile('[0-9a-z]{128}')
        assert value.search(r)

        r = self.callXmlrpc(raaFramework.pseudoroot.deleteRandomUser, 
                               'testuser')
        assert r
