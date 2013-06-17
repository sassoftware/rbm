#!/usr/bin/python
#
# Copyright (c) SAS Institute Inc.
#


import sys
from testrunner import suite


class Suite(suite.TestSuite):
    testsuite_module = sys.modules[__name__]
    topLevelStrip = 0

    def getCoverageDirs(self, handler, environ):
        import upsrv
        return [upsrv]


if __name__ == '__main__':
    Suite().run()
