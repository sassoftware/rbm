#
# Copyright (C) 2006 rPath, Inc.
# All rights reserved.
#
import cherrypy
import raatest
import raa.crypto
import os

from conary.repository.netrepos.netserver import ServerConfig
from conary import dbstore

import raa.service.lib
import raatest.service.tests.fakeclasses
from tests import webPluginTest, setupCnr
from rPath.conaryserver.srv.conaryserver import ConaryServer

key = raa.crypto.RSA.generate(1024, raa.crypto.prandFunc)

raaFramework = webPluginTest(
    preInit=lambda rt: setattr(rt, "serviceKey", key.publickey()))

raaFramework.pseudoroot = cherrypy.root.conaryserver.ConaryServer

class ConaryServerTest(raatest.rAATest):
    def __init__(self, *args, **kwargs):
        raatest.rAATest.__init__(self, *args, **kwargs)
        raa.service.lib.service = raatest.service.tests.fakeclasses.fakeServer()
        raa.service.lib.service.key = key

    def hideCnr(self):
        os.chmod(raaFramework.pseudoroot.cnrPath, 0000)

    def showCnr(self):
        os.chmod(raaFramework.pseudoroot.cnrPath, 0644)

    def setUp(self):
        raatest.rAATest.setUp(self)
        self.table = cherrypy.root.conaryserver.ConaryServer.table
        self.table.clear()
        raaFramework.pseudoroot.cnrPath = setupCnr()

        ConaryServer.__init__ = lambda *args: None
        self.conaryServer = ConaryServer()
        self.conaryServer.server = cherrypy.root.conaryserver.ConaryServer
        self.conaryServer.rootserver = cherrypy.root
        self.conaryServer.taskId = cherrypy.root.conaryserver.ConaryServer.taskId

    def tearDown(self):
        try:
            os.unlink(raaFramework.pseudoroot.cnrPath)
        except:
            pass
        raatest.rAATest.tearDown(self)

    def test_method(self):
        "the index method should return a string called now"
        import types
        result = self.callWithIdent(raaFramework.pseudoroot.index)
        assert type(result) == types.DictType

    def test_indextitle(self):
        "The mainpage should have the right title"
        self.requestWithIdent("/conaryserver/ConaryServer/")
        print cherrypy.response.body[0]
        assert "<title>update repository server names</title>" in cherrypy.response.body[0].lower()

        try:
            os.unlink(raaFramework.pseudoroot.cnrPath)
        except IOError:
            pass
        r = self.callWithIdent(raaFramework.pseudoroot.index)
        assert r['errorState'] == 'error' and \
            'could not read the configuration' in r['pageText']

    def test_setserver(self):
        self.table.setserver('localhost2')
        row = self.table.getRowsByColumns({})
        assert row == [{'srvname': 'localhost2'}]

        assert not self.table.setserver('localhost2')

    def test_clearserver(self):
        self.table.clearserver('localhost')
        row = self.table.getRowsByColumns({})
        assert row == []

    def test_getdata(self):
        self.table.setserver('localhost')
        assert self.table.getdata() == ['localhost']

    def test_countEntries(self):
        assert self.table.countEntries() == 0

    def test_refreshConaryRc(self):
        r = self.callWithIdent(raaFramework.pseudoroot.refreshConaryrc)
        assert r['errorState'] == 'guide'

    def test_delsrvname(self):
        r = self.callWithIdent(raaFramework.pseudoroot.delsrvname, 'localhost2')
        assert r == {'data': [], 'errorState': 'success',
            'pageText': 'Repository name "localhost2" deleted.'}

    def test_brokenDelsrvname(self):
        self.hideCnr()
        r = self.callWithIdent(raaFramework.pseudoroot.delsrvname, 'localhost2')
        assert r['errorState'] == 'error' and \
            'could not read the configuration' in r['pageText']
        self.showCnr()

    def test_setsrvname(self):
        r = self.callWithIdent(raaFramework.pseudoroot.setsrvname, 'localhost')
        assert r == {'data': [('localhost', True)], 'errorState': 'success',
            'pageText': 'Repository name updated.'}

        r = self.callWithIdent(raaFramework.pseudoroot.setsrvname, 'localhost2')
        assert r == {'data': [('localhost', True)], 'errorState': 'error',
            'pageText': 'Error:  Unable to update hostname.'}

    def test_brokenSetsrvname(self):
        self.hideCnr()
        r = self.callWithIdent(raaFramework.pseudoroot.setsrvname, 'localhost2')
        assert r['errorState'] == 'error' and \
            'could not read the configuration' in r['pageText']
        self.showCnr()

    def test_getData(self):
        r = self.callWithIdent(raaFramework.pseudoroot.getData)
        assert r == []

    def test_inUseRepository(self):
        # insert some fake data to prevent the server name removal
        cfg = ServerConfig()
        cfg.read(raaFramework.pseudoroot.cnrPath)

        db = dbstore.connect(cfg.repositoryDB[1], cfg.repositoryDB[0])
        cu = db.cursor()
        cu.execute("INSERT INTO Versions VALUES(1, '/localhost2@rpl:1')")
        cu.execute("INSERT INTO Instances VALUES(0, 0, 1, 0, 0, 0, 0, 0)")
        db.commit()
        db.close()

        r = self.callWithIdent(raaFramework.pseudoroot.delsrvname, 'localhost2')
        assert r == {'data': [], 'errorState': 'error',
            'pageText': 'Unable to delete repository name because it is in use.'}
