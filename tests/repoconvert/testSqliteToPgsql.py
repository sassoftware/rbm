#
# Copyright (C) 2006 rPath, Inc.
# All rights reserved.
#
import cherrypy
import tempfile
import os

from conary.repository.netrepos.netserver import ServerConfig
from conary import dbstore
from conary.server import schema

import unittest
import raatest
import raa.crypto
import raa.service.lib
import raatest.service.tests.fakeclasses
from tests import webPluginTest, setupCnr
from rPath.repoconvert.srv import repoconvert
import pgsql
import time
import types
import raa.db.schedule
from raa import constants, rpath_error

raaFramework = webPluginTest()
raaFramework.pseudoroot = cherrypy.root.repoconvert.SqliteToPgsql

def setupConfig():
    """Write a fake repository.cnr file and return the filename"""
    topdir = tempfile.mkdtemp('', 'sqlitetopgsql-config-')
    fd, fn = tempfile.mkstemp(dir=topdir)
    f = os.fdopen(fd, "w")

    fd, dbFn = tempfile.mkstemp(dir=topdir)
    os.close(fd)

    contentsdir = tempfile.mkdtemp(dir=topdir)
    includedir = tempfile.mkdtemp(dir=topdir)

    f.write("serverName localhost\n")
    f.write("repositoryDB sqlite %s\n" % dbFn)
    f.write('contentsDir    %s\n' % contentsdir)
    f.write('includeConfigFile  %s/*\n' % includedir)
    f.close()

    db = dbstore.connect(dbFn, "sqlite")
    schema.loadSchema(db)
    db.close()

    return (topdir, fn, includedir)

class runCommandStub(object):
    commandList = []

    def __init__(self):
        self.commandList = []
    def clear(self):
        self.commandList = []
    def __call__(self, *args, **kwargs):
        self.commandList.append((args, kwargs))

class SqliteToPgsqlTest(raatest.rAATest):
    def __init__(self, *args, **kwargs):
        raatest.rAATest.__init__(self, *args, **kwargs)
        raa.service.lib.service = raatest.service.tests.fakeclasses.fakeServer()

    def hideCnr(self):
        os.chmod(self.cfgPath, 0000)

    def showCnr(self):
        os.chmod(self.cfgPath, 0644)

    def setUp(self):
        raatest.rAATest.setUp(self)
        self.topdir, self.cfgPath, self.includedir = setupConfig()
        raaFramework.pseudoroot.cfgPath = self.cfgPath

        repoconvert.SqliteToPgsql.__init__ = lambda *args: None
        self.oldRunCommand = raa.lib.command.runCommand
        raa.lib.command.runCommand = runCommandStub()
        self.srvPlugin = repoconvert.SqliteToPgsql()
        self.srvPlugin.cfgPath = self.cfgPath
        self.srvPlugin.newCfgPath = os.path.join(self.includedir, 'db.cfg')
        self.srvPlugin.server = raaFramework.pseudoroot

        self.oldcallBackend = raaFramework.pseudoroot.callBackend
        raaFramework.pseudoroot.callBackend = lambda method, *args: \
            getattr(self.srvPlugin, method)(1, 1, *args)

    def tearDown(self):
        try:
            util.rmtree(self.topdir)
        except:
            pass
        raaFramework.pseudoroot.callBackend = self.oldcallBackend
        raatest.rAATest.tearDown(self)
        raa.lib.command.runCommand = self.oldRunCommand

    def _writeConvertedConfig(self, cfgPath):
        f = open(cfgPath, 'w')
        f.write('repositoryDB  postgresql foo@localhost/bar')
        f.close()

    def test_resetfinalized(self):
        #setup
        self._writeConvertedConfig(self.srvPlugin.newCfgPath)
        ret = self.callWithIdent(raaFramework.pseudoroot.finalize, confirm=True)
        self.assertEquals(ret, {'message': 'Conversion finalized'})
        os.unlink(self.srvPlugin.newCfgPath)

        #Do the test
        config = raaFramework.pseudoroot._getConfig()
        self.assertEquals(config['finalized'], False)

    def test_startPostgresql(self):
        oldconnect = dbstore.connect
        def raiseProgrammingError(x, y):
            raise pgsql.ProgrammingError('Fake')
        dbstore.connect=raiseProgrammingError
        oldsleep = time.sleep
        time.sleep = lambda x: None
        try:
            self.assertRaises(repoconvert.PreparationError, repoconvert._startPostgresql)
            self.assertEquals(len(raa.lib.command.runCommand.commandList), 1)

            raa.lib.command.runCommand.commandList=[]
            dbstore.connect = lambda x, y: None
            assert repoconvert._startPostgresql(), 'Did not return as expected'
            self.assertEquals(len(raa.lib.command.runCommand.commandList), 0)

            import epdb; epdb.stc('f')
            dbstore.connect=raiseProgrammingError
            def raiseErrorRunCommand(*x, **y):
                raise rpath_error.UnknownException('blah', 'blahblah')
            raa.lib.command.runCommand = raiseErrorRunCommand
            self.assertRaises(rpath_error.UnknownException, repoconvert._startPostgresql)
        finally:
            dbstore.connect = oldconnect
            time.sleep = oldsleep

    def test_getConfig(self):
        #Add two schedules, and start them
        sched = raa.db.schedule.ScheduleOnce()
        schedId1 = raaFramework.pseudoroot.schedule(sched)
        execId = cherrypy.root.execution.addExecution(schedId1, time.time(), status=constants.TASK_SCHEDULED)
        sched = raa.db.schedule.ScheduleOnce()
        schedId2 = raaFramework.pseudoroot.schedule(sched)
        execId = cherrypy.root.execution.addExecution(schedId2, time.time(), status=constants.TASK_RUNNING)

        config = raaFramework.pseudoroot._getConfig()
        self.assertEquals(config['running'], True)
        self.assertEquals(config['schedId'], schedId2)

    def test_method(self):
        "the index method should return a string called now"
        result = self.callWithIdent(raaFramework.pseudoroot.index)
        assert type(result) == types.DictType

    def test_finalize(self):
        res = self.callWithIdent(raaFramework.pseudoroot.finalize, False)
        assert res['error']
        res = self.callWithIdent(raaFramework.pseudoroot.finalize, True)
        assert res['message']
        self.assertEquals(True, raaFramework.pseudoroot.getPropertyValue('raa.hidden'))
        self.assertEquals(True, raaFramework.pseudoroot.getPropertyValue('FINALIZED'))

    def test_convert(self):
        res = self.callWithIdent(raaFramework.pseudoroot.convert, False)
        assert res['error']
        res = self.callWithIdent(raaFramework.pseudoroot.convert, True)
        assert res['schedId']

    def test_hideplugin(self):
        res = self.callWithIdent(raaFramework.pseudoroot.finalize, True)

        raaFramework.pseudoroot.initPlugin()
        self.assertEquals(raaFramework.pseudoroot.getPropertyValue('raa.hidden'), False)

        self._writeConvertedConfig(self.srvPlugin.newCfgPath)

        #The already converted case
        raaFramework.pseudoroot.initPlugin()
        self.assertEquals(raaFramework.pseudoroot.getPropertyValue('raa.hidden'), True)

        #The fresh install case
        raaFramework.pseudoroot.deletePropertyValue('FINALIZED')
        raaFramework.pseudoroot.initPlugin()
        self.assertEquals(raaFramework.pseudoroot.getPropertyValue('raa.hidden'), True)

    def test_indextitle(self):
        "The mainpage should have the right title"
        self.requestWithIdent("/repoconvert/SqliteToPgsql/")
        assert "<title>postgresql conversion - index</title>" in cherrypy.response.body[0].lower()

        assert "<h3>convert to postgresql</h3>" in cherrypy.response.body[0].lower()

    def _setupConvertScript(self, exitCode=0):
        fd, self.srvPlugin.convertScript = tempfile.mkstemp('.sh', 'testdbconversion-', dir=self.topdir)
        os.write(fd, 
"""#!/bin/sh

echo Fake script to convert the database 1>&2
sleep 4
for x in {0..9}; do
    echo Numbered output $x
done
touch %s/scriptrun
exit %d
""" % (self.topdir, exitCode))
        os.close(fd)

        os.chmod(self.srvPlugin.convertScript, 0700)

    def test_checkPlPgSQL(self):
        class fakeCursor(object):
            _exec = []
            _fetchOneRet = 1
            def execute(self, *args):
                self._exec.append(*args)
            def fetchone(self):
                return  [self._fetchOneRet]
        class fakeDbstore(object):
            def __init__(self, retval):
                self._retVal = retval
            def cursor(self):
                fcu = fakeCursor()
                fcu._fetchOneRet = self._retVal
                return fcu

        def fakeConnect(*a, **kw):
            return fakeDbstore(self.retVal)

        #setup
        self.retVal = 1
        oldconnect = dbstore.connect
        dbstore.connect = fakeConnect
        try:
            self.assertEquals(self.srvPlugin._checkPlPgSQL(), True)
            self.retVal = 0
            self.assertRaises(repoconvert.PreparationError, self.srvPlugin._checkPlPgSQL)
        finally:
            dbstore.connect = oldconnect

    def test_runConversion(self):
        self._setupConvertScript(2)
        oldreportMessage = self.srvPlugin.reportMessage
        self.srvPlugin.reportMessage = runCommandStub()
        try:
            self.assertRaises(repoconvert.ConversionError, self.srvPlugin._runConversion, 1)
        finally:
            self.srvPlugin.reportMessage = oldreportMessage

    def test_srvDoTask(self):
        self._setupConvertScript()
        sched = raa.db.schedule.ScheduleOnce()
        schedId = raaFramework.pseudoroot.schedule(sched)
        execId = cherrypy.root.execution.addExecution(schedId, time.time(), status=constants.TASK_RUNNING)
        oldreportMessage = self.srvPlugin.reportMessage
        self.srvPlugin.reportMessage = runCommandStub()
        oldchkpgsql = self.srvPlugin._checkPlPgSQL
        self.srvPlugin._checkPlPgSQL = types.MethodType(lambda x: None, self.srvPlugin, repoconvert.SqliteToPgsql)
        try:
            self.srvPlugin.doTask(execId, schedId)

            #check to see that stuff got run
            # Should have run both httpd stop and httpd start
            self.assertEqual(len(raa.lib.command.runCommand.commandList), 2)

            assert os.path.isfile(os.path.join(self.topdir, 'scriptrun'))
            assert os.path.isfile(self.srvPlugin.newCfgPath)
            self.assertEquals(self.srvPlugin.reportMessage.commandList[0][0][1], 'Shutting down httpd')
            self.assertEquals(self.srvPlugin.reportMessage.commandList[1][0][1], 'Checking that PostgreSQL is running, and if not, starting it')
            self.assertEquals(self.srvPlugin.reportMessage.commandList[2][0][1], 'Running database conversion script')
            self.assertEquals(self.srvPlugin.reportMessage.commandList[-2][0][1], 'Conversion completed successfully')
            self.assertEquals(self.srvPlugin.reportMessage.commandList[-1][0][1], 'Starting httpd')
            otheroutput = ''.join([x[0][1] for x in self.srvPlugin.reportMessage.commandList[3:-2]])
            assert otheroutput.startswith('Fake script to convert the database')
            assert otheroutput.endswith('Numbered output 5\nNumbered output 6\nNumbered output 7\nNumbered output 8\nNumbered output 9')
        finally:
            self.srvPlugin.reportMessage = oldreportMessage
            self.srvPlugin._checkPlPgSQL = self.srvPlugin._checkPlPgSQL

