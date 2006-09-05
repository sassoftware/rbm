#
# Copyright (C) 2006 rPath, Inc.
# All rights reserved.
#
import cherrypy
import raatest

from tests import webPluginTest
raaFramework = webPluginTest()
raaFramework.pseudoroot = cherrypy.root.mirrorusers.MirrorUsers


class MirroUsersTest(raatest.rAATest):
    def setUp(self):
        raatest.rAATest.setUp(self)
        self.table = cherrypy.root.mirrorusers.MirrorUsers.table
        self.table.clear()

    def test_setdata(self):
        self.table.setdata(0, 'testuser', 'permission', 'password', 'test')

        assert self.table.getdata(0) == \
            [{'operation': 'test', 'password': 'password', 'user': 'testuser', 'permission': 'permission'}]

    def test_indextitle(self):
        self.requestWithIdent("/mirrorusers/MirrorUsers/")
        print cherrypy.response.body[0]
        assert "<title>disk usage</title>" in cherrypy.response.body[0].lower()

