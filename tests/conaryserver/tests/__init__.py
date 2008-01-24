#
# Copyright (C) 2006 rPath, Inc.
# All rights reserved.
#
import cherrypy
import tempfile
import os

from conary.repository.netrepos.netserver import ServerConfig
from conary import dbstore

import raatest
import raa.crypto
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
        self.conaryServer.cnrPath = raaFramework.pseudoroot.cnrPath
        fd, self.conaryServer.conaryrcPath = tempfile.mkstemp()
        os.close(fd)
        self.conaryServer.apacheRestart = ['/bin/false']

        self.oldcallBackend = raaFramework.pseudoroot.callBackend
        raaFramework.pseudoroot.callBackend = lambda method, *args: \
            getattr(self.conaryServer, method)(1, 1, *args)

    def tearDown(self):
        try:
            os.unlink(raaFramework.pseudoroot.cnrPath)
        except:
            pass
        try:
            os.unlink(self.conaryServer.conaryrcPath)
        except:
            pass
        raaFramework.pseudoroot.callBackend = self.oldcallBackend
        raatest.rAATest.tearDown(self)

    def test_backend(self):
        cfg = ServerConfig()
        cfg.forceSSL = True
        fd = open(raaFramework.pseudoroot.cnrPath, 'w')
        cfg.display(fd)
        fd.close()
        try:
            oldGenFile = self.conaryServer.generatedFile
            tmpFd, tmpFile = tempfile.mkstemp()
            os.close(tmpFd)
            self.conaryServer.generatedFile = tmpFile
            genCfg = ServerConfig()
            genCfg.read(self.conaryServer.generatedFile)
            genCfg.logFile = 'this is a test'
            genCfg.repositoryDB = ('testdb', 'testpath')
            fd = open(self.conaryServer.generatedFile, 'w')
            genCfg.displayKey('logFile', out=fd)
            genCfg.displayKey('repositoryDB', out=fd)
            fd.close()
            self.table.setserver('localhost2')
            r = self.conaryServer.updateServerNames(0, 1, self.table.getdata())
            fd = open(tmpFile)
            cfgLines = fd.readlines()
            fd.close()
            genCfg.read(tmpFile)
            assert len(cfgLines) == 3
            assert genCfg.repositoryDB == ('testdb', 'testpath')
            assert 'this is a test' in genCfg.logFile
            assert os.path.exists(self.conaryServer.conaryrcPath)
            fd = open(self.conaryServer.conaryrcPath)
            data = fd.read()
            fd.close()
            assert 'https' in data
            cfg.forceSSL = False
            fd = open(raaFramework.pseudoroot.cnrPath, 'w')
            cfg.display(fd)
            fd.close()
            self.table.setserver('localhost3')
            r = self.conaryServer.updateServerNames(0, 1, self.table.getdata())
            fd = open(self.conaryServer.conaryrcPath)
            data = fd.read()
            fd.close()
            assert 'https' not in data
            assert 'http' in data
        finally:
            self.conaryServer.generatedFile = oldGenFile


    def test_method(self):
        "the index method should return a string called now"
        import types
        result = self.callWithIdent(raaFramework.pseudoroot.index)
        assert type(result) == types.DictType

    def test_indextitle(self):
        "The mainpage should have the right title"
        self.requestWithIdent("/conaryserver/ConaryServer/")
        assert "<title>update repository hostnames</title>" in cherrypy.response.body[0].lower()

        try:
            os.unlink(raaFramework.pseudoroot.cnrPath)
        except IOError:
            pass
        r = self.callWithIdent(raaFramework.pseudoroot.index)
        assert r['errorState'] == 'error' and \
            'not read the configuration' in r['pageText']

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
            'not read the configuration' in r['pageText']
        self.showCnr()

    def test_setsrvname(self):
        r = self.callWithIdent(raaFramework.pseudoroot.setsrvname, 'localhost')
        assert r == {'data': [('localhost', True)], 'errorState': 'success',
            'pageText': 'Repository name updated.'}

        r = self.callWithIdent(raaFramework.pseudoroot.setsrvname, 'localhost2')
        assert r == {'data': [('localhost', True)], 'errorState': 'error',
            'pageText': 'Error:  Unable to update hostname.'}

        r = self.callWithIdent(raaFramework.pseudoroot.setsrvname, '')
        self.assertEquals({'data': [('localhost', True)], 'errorState': 'error',
            'pageText': "Blank hostname entered."}, r)

    def test_brokenSetsrvname(self):
        self.hideCnr()
        r = self.callWithIdent(raaFramework.pseudoroot.setsrvname, 'localhost2')
        assert r['errorState'] == 'error' and \
            'not read the configuration' in r['pageText']
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

    def test_addServerName(self):
        r = self.callXmlrpc(raaFramework.pseudoroot.addServerName, 'testserver')
        
        res = self.table.getdata()
        assert 'testserver' in res 
        assert res.count('testserver') == 1
        r = self.callXmlrpc(raaFramework.pseudoroot.addServerName, 'testserver')
        assert r
        res = self.table.getdata()
        assert 'testserver' in res 
        assert res.count('testserver') == 1

        r = self.callXmlrpc(raaFramework.pseudoroot.addServerName, 'testserver2')
        res = self.table.getdata()
        assert 'testserver' in res 
        assert res.count('testserver') == 1
        assert 'testserver2' in res 
        assert res.count('testserver2') == 1

        r = self.callXmlrpc(raaFramework.pseudoroot.addServerName, ['test3',
                            'test4', 'test5'])
        res = self.table.getdata()
        assert res == ['testserver', 'testserver2', 'test3', 'test5', 'test4']
        r = self.callXmlrpc(raaFramework.pseudoroot.addServerName, ['test3',
                            'test4', 'test5'])
        res = self.table.getdata()
        assert res == ['testserver', 'testserver2', 'test3', 'test5', 'test4']

    def test_addServerName2(self):
        self.hideCnr()
        r = self.callXmlrpc(raaFramework.pseudoroot.addServerName, 'testserver')
        assert not r

    def test_delServerName(self):
        r = self.callXmlrpc(raaFramework.pseudoroot.addServerName, 'testserver')
        r = self.callXmlrpc(raaFramework.pseudoroot.addServerName, 'testserver2')
        res = self.table.getdata()
        assert 'testserver' in res 
        r = self.callXmlrpc(raaFramework.pseudoroot.delServerName, 'testserver')
        res = self.table.getdata()
        assert 'testserver' not in res
        assert 'testserver2' in res

        cfg = ServerConfig()
        cfg.read(raaFramework.pseudoroot.cnrPath)

        db = dbstore.connect(cfg.repositoryDB[1], cfg.repositoryDB[0])
        cu = db.cursor()
        cu.execute("INSERT INTO Versions VALUES(1, '/testserver2@rpl:1')")
        cu.execute("INSERT INTO Instances VALUES(0, 0, 1, 0, 0, 0, 0, 0)")
        db.commit()
        db.close()

        r = self.callXmlrpc(raaFramework.pseudoroot.delServerName, 'testserver')
        assert r

    def test_delServerName2(self):
        r = self.callXmlrpc(raaFramework.pseudoroot.addServerName, 'testserver')
        res = self.table.getdata()
        assert 'testserver' in res 
        self.hideCnr()
        r = self.callXmlrpc(raaFramework.pseudoroot.delServerName, 'testserver')
        assert not r

    def test_delServerName3(self):
        self.table.setserver('testserver2')
        res = self.table.getdata()
        assert 'testserver2' in res 
        r = self.callXmlrpc(raaFramework.pseudoroot.delServerName, 'testserver2')
        assert r
        self.assertEquals(self.table.getdata(), [])
