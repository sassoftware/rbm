#
# Copyright (C) 2006 rPath, Inc.
# All rights reserved.
#
import cherrypy
import raatest
import os
from tests import webPluginTest, setupCnr

raaFramework = webPluginTest()
raaFramework.pseudoroot = cherrypy.root.reaentitlement.rEAEntitlement


class rEAEntitlementTest(raatest.rAATest):
    def setUp(self):
        raatest.rAATest.setUp(self)
        self.table = cherrypy.root.reaentitlement.rEAEntitlement.table
        self.table.clear()
        raaFramework.pseudoroot.cnrPath = setupCnr()

    def tearDown(self):
        try:
            os.unlink(raaFramework.pseudoroot.cnrPath)
        except:
            pass
        raatest.rAATest.tearDown(self)

    def test_keys(self):
        assert(self.table.getkey() == "")
        self.table.setkey("thisismykey")
        assert(self.table.getkey() == "thisismykey")

    def test_index(self):
        r = self.requestWithIdent("/reaentitlement/rEAEntitlement/")
        assert "<title>manage administrative entitlement</title>" in cherrypy.response.body[0].lower()

    def test_setkey(self):
        r = self.callWithIdent(raaFramework.pseudoroot.setkey, key = "thisismykey")
        assert r == {'key': 'thisismykey'}
