#
# Copyright (C) 2006 rPath, Inc.
# All rights reserved.
#
import cherrypy
import raatest

from tests import webPluginTest
raaFramework = webPluginTest()
raaFramework.pseudoroot = cherrypy.root.reaentitlement.rEAEntitlement


class rEAEntitlementTest(raatest.rAATest):
    pass
