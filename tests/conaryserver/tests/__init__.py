#
# Copyright (C) 2006 rPath, Inc.
# All rights reserved.
#
import cherrypy
import raatest
import raa.crypto

import raa.service.lib
import raatest.service.tests.fakeclasses
from tests import webPluginTest
from rPath.conaryserver.srv.conaryserver import ConaryServer

key = raa.crypto.RSA.generate(1024, raa.crypto.prandFunc)

raaFramework = webPluginTest(
    preInit=lambda rt: setattr(rt, "serviceKey", key.publickey()))

raaFramework.pseudoroot = cherrypy.root.conaryserver.ConaryServer

def setupCnr():
    import tempfile
    import os

    fd, fn = tempfile.mkstemp()
    f = os.fdopen(fd, "w")

    f.write("serverName localhost")
    f.close()

    return fn

class ConaryServerTest(raatest.rAATest):
    def __init__(self, *args, **kwargs):
        raatest.rAATest.__init__(self, *args, **kwargs)
        raa.service.lib.service = raatest.service.tests.fakeclasses.fakeServer()
        raa.service.lib.service.key = key

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

    def test_setserver(self):
        self.table.setserver('localhost2')
        row = self.table.getRowsByColumns({})
        assert row == [{'srvname': 'localhost2'}]

    def test_clearserver(self):
        self.table.clearserver('localhost')
        row = self.table.getRowsByColumns({})
        assert row == []

    def test_getdata(self):
        self.table.setserver('localhost')
        assert self.table.getdata() == ['localhost']

    def test_countEntries(self):
        assert self.table.countEntries() == 0
