#
# Copyright (C) 2006 rPath, Inc.
# All rights reserved.
#
import cherrypy
import raatest

import rPath
import re

from tests import webPluginTest, setupCnr

from rPath.mirrorusers.srv.mirrorusers import MirrorUsers

raaFramework = webPluginTest()
raaFramework.pseudoroot = cherrypy.root.mirrorusers.MirrorUsers


class MirrorUsersTest(raatest.rAATest):
    def setUp(self):
        raatest.rAATest.setUp(self)
        raaFramework.pseudoroot.cnrPath = setupCnr()

        MirrorUsers.__init__ = lambda *args: None
        self.srvPlugin = MirrorUsers()
        self.srvPlugin.cnrPath = raaFramework.pseudoroot.cnrPath

        self.oldcallBackend = raaFramework.pseudoroot.callBackend
        raaFramework.pseudoroot.callBackend = lambda method, *args: \
            getattr(self.srvPlugin, method)(1, 1, *args)

    def tearDown(self):
        raatest.rAATest.tearDown(self)
        try:
            os.unlink(raaFramework.pseudoroot.cnrPath)
        except:
            pass
        raaFramework.pseudoroot.callBackend = self.oldcallBackend

    def test_indexTitle(self):
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
        self.assertEqual(result, {'errors': 'Passwords do not match. Please try again.', 'error': True})

        # test for blank username
        result = self.callWithIdent(raaFramework.pseudoroot.add,
            username = '', passwd1 = 'pass', passwd2 = 'pass')
        self.assertEqual(result, {'errors': 'Please enter a user name.', 'error': True})

        # test for bogus anonymous username
        result = self.callWithIdent(raaFramework.pseudoroot.add,
            username = 'anonymous', passwd1 = 'pass', passwd2 = 'pass',
            perm = 'not anonymous')
        self.assertEqual(result, {'errors': 'The user name "anonymous" is reserved.  '
            'Please choose a different user name.', 'error': True})

        # test for success
        result = self.callWithIdent(raaFramework.pseudoroot.add,
            username = 'newuser', passwd1 = 'pass', passwd2 = 'pass')
        self.assertEquals(result, {'message': 'User "newuser" added with Anonymous permission.', 'error': False})

        # test for duplicate user
        result = self.callWithIdent(raaFramework.pseudoroot.add,
            username = 'newuser', passwd1 = 'pass', passwd2 = 'pass')
        self.assertEquals( result, {'errors': 'User "newuser" already exists. '
            ' Please choose a different user name.', 'error': True})

    def test_addUser2(self):
        result = self.callWithIdent(raaFramework.pseudoroot.add,
            username = 'anonymous', passwd1 = 'pass', passwd2 = 'pass')
        self.assertEquals(result, {'message': 'User "anonymous" added with Anonymous permission.', 'error': False})

        result = self.callWithIdent(raaFramework.pseudoroot.add,
            username = 'newAdmin', passwd1 = 'pass', passwd2 = 'pass',
            perm = 'Admin')
        self.assertEquals(result, {'message': 'User "newAdmin" added with Admin permission.', 'error': False})

        result = self.callWithIdent(raaFramework.pseudoroot.add,
            username = 'newMirror', passwd1 = 'pass', passwd2 = 'pass',
            perm = 'Mirror')
        self.assertEquals(result, {'message': 'User "newMirror" added with Mirror permission.', 'error': False})

    def test_index(self):
        result = self.callWithIdent(raaFramework.pseudoroot.add,
            username = 'anonymous', passwd1 = 'pass', passwd2 = 'pass')
        result = self.callWithIdent(raaFramework.pseudoroot.add,
            username = 'newAdmin', passwd1 = 'pass', passwd2 = 'pass',
            perm = 'Admin')
        result = self.callWithIdent(raaFramework.pseudoroot.add,
            username = 'newMirror', passwd1 = 'pass', passwd2 = 'pass',
            perm = 'Mirror')
        result = self.callWithIdent(raaFramework.pseudoroot.add,
            username = 'newUser', passwd1 = 'pass', passwd2 = 'pass')

        result = self.callWithIdent(raaFramework.pseudoroot.index)
        assert {'user': 'newAdmin', 'permission': 'Admin'} in result['userList']
        assert {'user': 'newMirror', 'permission': 'Mirroring'} in result['userList']
        assert {'user': 'newUser', 'permission': 'Read-Only'} in result['userList']
        assert {'user': 'anonymous', 'permission': 'Anonymous'} in result['userList']

    def test_deleteUser(self):
        result = self.callWithIdent(raaFramework.pseudoroot.deleteUser, 'newuser')
        assert result == {'username': 'newuser'}

        result = self.callWithIdent(raaFramework.pseudoroot.add,
            username = 'newuser', passwd1 = 'pass', passwd2 = 'pass')
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

    def test_addRandomness(self):
        r = self.callXmlrpc(raaFramework.pseudoroot.addRandomUser, 
                               'testuser')
        value = re.compile('[0-9a-z]{128}')
        assert value.search(r)

        r = self.callXmlrpc(raaFramework.pseudoroot.deleteRandomUser, 
                               'testuser')
        assert r

    def test_migrate(self):
        db = raaFramework.pseudoroot.pluginProperties.db
        cu = db.cursor()
        cu.execute("CREATE TABLE plugin_rpath_MirrorTable (col TEXT)")
        db.loadSchema()

        raaFramework.pseudoroot.initPlugin()

        db.loadSchema()

        assert 'plugin_rpath_MirrorTable' not in db.tables
