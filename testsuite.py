#!/usr/bin/python2.4
#
# Copyright (c) 2008 rPath, Inc.
#
import os
import sys

import testhelp
from conary_test import resources
from conary_test import runner

class TestSuiteHandler(testhelp.TestSuiteHandler):
    def __init__(self, *args, **kw):
        self.pluginPath = kw.pop('pluginPath')
        testhelp.TestSuiteHandler.__init__(self, *args, **kw)

    def getCoverageDirs(self, environ):
        return os.path.join(self.pluginPath)

    def getCoverageExclusions(self, environ):
        return ['tests/.*']


def main(argv, individual=True):
    runner.setup()
    kw = dict(pluginPath=os.getcwd() + '/raaplugins')
    return runner.main(argv, individual=individual,
                       handlerClass=TestSuiteHandler, handlerKw=kw)


# These should not be set, they're here to placate the conary testsuite
from conary_test.runner import TestCase, setup, isIndividual
archivePath = None
testPath = None
conaryDir = None


if __name__ == '__main__':
    main(sys.argv, individual=False)
