#
# Copyright (C) 2006 rPath, Inc.
# All rights reserved.
#
import cherrypy
import raatest

from tests import webPluginTest
raaFramework = webPluginTest()
raaFramework.pseudoroot = cherrypy.root.diskusage.DiskUsage


class DiskUsageTest(raatest.rAATest):
    def test_method(self):
        "the index method should return a string called now"
        import types
        result = self.callWithIdent(raaFramework.pseudoroot.index)
        assert type(result) == types.DictType

    def test_indextitle(self):
        "The mainpage should have the right title"
        self.requestWithIdent("/diskusage/DiskUsage/")
        print cherrypy.response.body[0]
        assert "<title>disk usage</title>" in cherrypy.response.body[0].lower()
