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
from tests import webPluginTest

key = raa.crypto.RSA.generate(1024, raa.crypto.prandFunc)

raaFramework = webPluginTest(
    preInit=lambda rt: setattr(rt, "serviceKey", key.publickey()))

raaFramework.pseudoroot = cherrypy.root.conaryserver.ConaryServer

class ConaryServerTest(raatest.rAATest):
    def __init__(self, *args, **kwargs):
        raatest.rAATest.__init__(self, *args, **kwargs)
        raa.service.lib.service = raatest.service.tests.fakeclasses.fakeServer()
        raa.service.lib.service.key = key

    def test_addServerName(self):
        r = self.callXmlrpc(raaFramework.pseudoroot.addServerName, 'testserver')
        assert r

    def test_delServerName(self):
        r = self.callXmlrpc(raaFramework.pseudoroot.addServerName, 'testserver')
        assert r
