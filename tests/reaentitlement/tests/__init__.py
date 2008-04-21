#
# Copyright (C) 2006 rPath, Inc.
# All rights reserved.
#
import cherrypy
import raatest
import os
from tests import webPluginTest, setupCnr
from conary.repository.netrepos.netserver import ServerConfig
from conary.repository.netrepos.netserver import NetworkRepositoryServer

from rPath.reaentitlement.srv.reaentitlement import rEAEntitlement as rEAEntitlementSrv
from rPath.reaentitlement.web.reaentitlement import ENTITLEMENT_KEY

raaFramework = webPluginTest()
raaFramework.pseudoroot = cherrypy.root.reaentitlement.rEAEntitlement


class rEAEntitlementTest(raatest.rAATest):
    def setUp(self):
        raatest.rAATest.setUp(self)
        raaFramework.pseudoroot.cnrPath = setupCnr()

        rEAEntitlementSrv.__init__ = lambda *a: None
        self.srvPlugin = rEAEntitlementSrv()
        self.srvPlugin.cnrPath = raaFramework.pseudoroot.cnrPath

        self.oldcallBackend = raaFramework.pseudoroot.callBackend
        raaFramework.pseudoroot.callBackend = lambda method, *args: \
            getattr(self.srvPlugin, method)(1, 1, *args)

    def tearDown(self):
        try:
            os.unlink(raaFramework.pseudoroot.cnrPath)
        except:
            pass
        raaFramework.pseudoroot.callBackend = self.oldcallBackend
        raatest.rAATest.tearDown(self)

    def test_index(self):
        r = self.requestWithIdent("/reaentitlement/rEAEntitlement/")
        assert "<title>manage administrative entitlement</title>" in cherrypy.response.body[0].lower()

    def test_setkey(self):
        managementClass = 'management'
        managementRole = 'admin'

        r = self.callWithIdent(raaFramework.pseudoroot.setkey, key = "thisismykey")
        assert r['key'] == 'thisismykey'
        assert r.has_key('serverNames')
        assert r.has_key('hostName')

        #Now make sure that that entitlement got added to the server
        cfg = ServerConfig()
        cfg.read(self.srvPlugin.cnrPath)
        nr = NetworkRepositoryServer(cfg, self.srvPlugin.reposserver)

        authtoken = ('anonymous', 'anonymous', [(managementClass, 'thisismykey')])
        assert nr.auth.authCheck(authtoken, admin=True)
        self.assertEquals(
            nr.auth.iterEntitlementKeys(authtoken, managementClass),
            ['thisismykey'])
        self.assertEquals(
            nr.auth.getEntitlementClassesRoles(authtoken, [managementClass]),
            {managementClass: [managementRole]})
        self.assertEquals(nr.auth.getRoleList(), [managementRole])

        #Set another key
        r = self.callWithIdent(raaFramework.pseudoroot.setkey, key = "thisismyotherkey")
        assert r['key'] == 'thisismyotherkey'
        authtoken = ('anonymous', 'anonymous', [(managementClass, 'thisismyotherkey')])
        assert nr.auth.authCheck(authtoken, admin=True)

    def test_migrate(self):
        db = raaFramework.pseudoroot.pluginProperties.db
        cu = db.cursor()
        cu.execute("CREATE TABLE plugin_rpath_rEAEntitlementTable (ent_key TEXT)")
        cu.execute("INSERT INTO plugin_rpath_rEAEntitlementTable (ent_key) VALUES ('migrateme')")
        db.loadSchema()

        raaFramework.pseudoroot.setPropertyValue(ENTITLEMENT_KEY, 'beforemigrate')

        raaFramework.pseudoroot.initPlugin()
        db.loadSchema()

        assert 'plugin_rpath_rEAEntitlementTable' not in db.tables
        self.assertEquals(raaFramework.pseudoroot.getPropertyValue(ENTITLEMENT_KEY), 'migrateme')

