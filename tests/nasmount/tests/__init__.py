#
# Copyright (C) 2007 rPath, Inc.
# All rights reserved.
#
import cherrypy
import os
import raatest
import tempfile

import rPath

from tests import webPluginTest
raaFramework = webPluginTest()
raaFramework.pseudoroot = cherrypy.root.nasmount.NasMount

from conary.lib import util

import rPath.nasmount.srv.nasmount

rPath.nasmount.srv.nasmount.NasMount.__init__ = lambda *args, **kwargs: None

from raa.lib import mount
mount.mount = lambda *args, **kwargs: None


class NasTest(raatest.rAATest):
    def __init__(self, *args, **kwargs):
        raatest.rAATest.__init__(self, *args, **kwargs)
        self._mockedFuncs = []

    def mock(self, funcName, func = lambda *args, **kwargs: None):
        self._mockedFuncs.append(funcName)
        raaFramework.pseudoroot.__dict__[funcName] = func

    def cherryCall(self, funcName, *args, **kwargs):
        func = cherrypy.root.nasmount.NasMount.__getattribute__(funcName)
        return self.callWithIdent(func, *args, **kwargs)

    def setUp(self):
        raatest.rAATest.setUp(self)
        raaFramework.pseudoroot.errors = []
        raaFramework.pseudoroot.messages = []
        fd, self.fstab = tempfile.mkstemp()
        os.close(fd)
        rPath.nasmount.srv.nasmount.FSTAB = self.fstab

    def tearDown(self):
        raatest.rAATest.tearDown(self)
        for funcName in self._mockedFuncs:
            del raaFramework.pseudoroot.__dict__[funcName]
        self._mockedFuncs = []
        util.rmtree(self.fstab)

    def testMissingParams(self):
        self.mock('_setMount')
        try:
            res = self.cherryCall('setMount')
        except cherrypy.HTTPRedirect, e:
            pass

        assert raaFramework.pseudoroot.errors == \
            ['Parameter Error: server is missing',
             'Parameter Error: remoteMount is missing'], \
             "parameters allowed to be empty"

    def testMissingServer(self):
        self.mock('_setMount')
        try:
            res = self.cherryCall('setMount', remoteMount = '/test')
        except cherrypy.HTTPRedirect, e:
            pass

        assert raaFramework.pseudoroot.errors == \
            ['Parameter Error: server is missing'], \
            "server param allowed to be empty"

    def testMissingRMount(self):
        self.mock('_setMount')
        try:
            res = self.cherryCall('setMount', server = 'test')
        except cherrypy.HTTPRedirect, e:
            pass

        assert raaFramework.pseudoroot.errors == \
            ['Parameter Error: remoteMount is missing'], \
            "remoteMount param allowed to be empty"

    def testCorrectParams(self):
        self.mock('_setMount')

        try:
            res = self.cherryCall('setMount', server = 'test',
                                  remoteMount = '/test')
        except cherrypy.HTTPRedirect, e:
            pass

        assert raaFramework.pseudoroot.errors == [], "no errors expecte"

    def testBackendGood(self):
        self.mock('callBackend', lambda *args, **kwargs: (False, ''))

        raaFramework.pseudoroot._setMount('test', '/test', '/moutnPoint')

        assert raaFramework.pseudoroot.messages == \
            ['Sucessfully set remote contents store']

    def testBackendBad(self):
        self.mock('callBackend', lambda *args, **kwargs: (True, 'SENTINEL'))

        raaFramework.pseudoroot._setMount('test', '/test', '/moutnPoint')

        assert raaFramework.pseudoroot.errors == ['SENTINEL']

    def testIndexBadMount(self):
        self.mock('callBackend', lambda *args, **kwargs: (True, 'SENTINEL'))

        res = self.cherryCall('index')

        assert res == {'errors': ['SENTINEL'],
                       'messages': [],
                       'remoteMount': '',
                       'server': ''}

        # also test the effect of marshallMessages
        raaFramework.pseudoroot.errors == []

    def testIndexEmptyMount(self):
        self.mock('callBackend', lambda *args, **kwargs: (False, ('', '')))

        res = self.cherryCall('index')

        assert res == {'errors': [],
                       'messages': [],
                       'remoteMount': '',
                       'server': ''}

    def testIndexGoodMount(self):
        self.mock('callBackend', lambda *args, **kwargs: (False,
                                                          ('srvr', 'mnt')))

        res = self.cherryCall('index')

        assert res == {'errors': [],
                       'messages': [],
                       'remoteMount': 'mnt',
                       'server': 'srvr'}

    # back end tests
    def testGetMissingMount(self):
        nas = rPath.nasmount.srv.nasmount.NasMount()

        res = nas.getMount(0,0, 'test')

        assert res == (False, ('', ''))

    def testGetMount(self):
        nas = rPath.nasmount.srv.nasmount.NasMount()

        f = open(self.fstab, 'w')
        f.write('/dev/proc /proc proc defaults 0 0\n')
        f.write('testSrv:testMnt /mountPoint nfs defaults 0 0\n')
        f.close()

        res = nas.getMount(0, 0, '/mountPoint')

        assert res == (False, ('testSrv', 'testMnt'))

    def testLocalMount(self):
        nas = rPath.nasmount.srv.nasmount.NasMount()

        f = open(self.fstab, 'w')
        f.write('/dev/proc /proc proc defaults 0 0\n')
        f.write('testMnt /mountPoint nfs defaults 0 0\n')
        f.close()

        res = nas.getMount(0,0, '/mountPoint')

        assert res == (False, ('', 'testMnt'))

    def testMissingMount(self):
        nas = rPath.nasmount.srv.nasmount.NasMount()
        res = nas.setMount(0, 0, 'testSrv', 'testMnt', 'badMount')

        assert res == (True, 'Mount Point: badMount does not exist\n')

    def testSetMount(self):
        nas = rPath.nasmount.srv.nasmount.NasMount()
        tmpDir = tempfile.mkdtemp()

        f = open(self.fstab, 'w')
        f.write('/dev/proc /proc proc defaults 0 0\n')
        f.close()

        try:
            res = nas.setMount(0, 0, 'testSrv', 'testMnt', tmpDir)
        finally:
            util.rmtree(tmpDir)

        assert res == (False, '')
        f = open(self.fstab)

        assert f.read() == '/dev/proc /proc proc defaults 0 0\n' \
            'testSrv:testMnt %s nfs defaults 0 0\n' % tmpDir
        f.close()

    def testEmptyFsTab(self):
        nas = rPath.nasmount.srv.nasmount.NasMount()
        tmpDir = tempfile.mkdtemp()

        try:
            res = nas.setMount(0, 0, 'testSrv', 'testMnt', tmpDir)
        finally:
            util.rmtree(tmpDir)

        assert res == (False, '')

        f = open(self.fstab)
        assert f.read() == 'testSrv:testMnt %s nfs defaults 0 0\n' % tmpDir
        f.close()

    def testRemoteMounted(self):
        nas = rPath.nasmount.srv.nasmount.NasMount()
        tmpDir = tempfile.mkdtemp()

        isMounted = rPath.nasmount.srv.nasmount.isMounted
        rPath.nasmount.srv.nasmount.isMounted = lambda *args, **kwargs: True

        try:
            res = nas.setMount(0, 0, 'testSrv', 'testMnt', tmpDir)
        finally:
            rPath.nasmount.srv.nasmount.isMounted = isMounted
            util.rmtree(tmpDir)

        assert res == (True, 'testMnt is already mounted\n')

    def testLocalMounted(self):
        def newIsMounted(path):
            return path != 'testMnt'

        nas = rPath.nasmount.srv.nasmount.NasMount()
        tmpDir = tempfile.mkdtemp()

        isMounted = rPath.nasmount.srv.nasmount.isMounted
        rPath.nasmount.srv.nasmount.isMounted = newIsMounted

        try:
            res = nas.setMount(0, 0, 'testSrv', 'testMnt', tmpDir)
        finally:
            rPath.nasmount.srv.nasmount.isMounted = isMounted
            util.rmtree(tmpDir)

        assert res == (True, '%s is already mounted\n' % tmpDir)

    def testDirNotEmpty(self):
        nas = rPath.nasmount.srv.nasmount.NasMount()
        tmpDir = tempfile.mkdtemp()
        fd, tmpFile = tempfile.mkstemp(dir = tmpDir)
        os.close(fd)

        try:
            res = nas.setMount(0, 0, 'testSrv', 'testMnt', tmpDir)
        finally:
            util.rmtree(tmpDir)

        assert res == (True, '%s is not empty\n' % tmpDir)

    def testBadSever(self):
        nas = rPath.nasmount.srv.nasmount.NasMount()
        tmpDir = tempfile.mkdtemp()

        try:
            res = nas.setMount(0, 0, 'bad-serverName;', 'testMnt', tmpDir)
        finally:
            util.rmtree(tmpDir)

        assert res == (True, "'bad-serverName;' must be a FQDN\n")

    def testBadMount(self):
        nas = rPath.nasmount.srv.nasmount.NasMount()
        tmpDir = tempfile.mkdtemp()

        try:
            res = nas.setMount(0, 0, 'testSrv', 'testMnt;', tmpDir)
        finally:
            util.rmtree(tmpDir)

        assert res == (True,
                       "'testMnt;' cannot contain string or shell delimiters\n")

    def testMissingFstab(self):
        rPath.nasmount.srv.nasmount.FSTAB = 'doesnt_exist'
        nas = rPath.nasmount.srv.nasmount.NasMount()

        try:
            nas.mkFstabEntry('testSrv', 'testMnt', 'localMnt')
        except AssertionError, e:
            assert str(e) == '/etc/fstab does not exist\n'

    def testRemotePresent(self):
        nas = rPath.nasmount.srv.nasmount.NasMount()
        f = open(self.fstab, 'w')
        f.write('testSrv:testMnt somemount nfs defaults 0 0\n')
        f.close()

        try:
            nas.mkFstabEntry('testSrv', 'testMnt', 'localMnt')
        except AssertionError, e:
            assert str(e) == 'Remote Mount: ' \
                'testSrv:testMnt is already present in /etc/fstab\n'

    def testLocalPresent(self):
        nas = rPath.nasmount.srv.nasmount.NasMount()
        f = open(self.fstab, 'w')
        f.write('testSrv:testRemMnt localMnt nfs defaults 0 0\n')
        f.close()

        try:
            nas.mkFstabEntry('testSrv', 'testMnt', 'localMnt')
        except AssertionError, e:
            assert str(e) == 'Local Mount: ' \
                'localMnt already in /etc/fstab\n'

    def testFStabNewline(self):
        nas = rPath.nasmount.srv.nasmount.NasMount()
        f = open(self.fstab, 'w')
        f.write('/dev/proc /proc proc defaults 0 0')
        f.close()

        nas.mkFstabEntry('testSrv', 'testMnt', 'localMnt')


        f = open(self.fstab)
        assert f.read() == '/dev/proc /proc proc defaults 0 0\n' \
            'testSrv:testMnt localMnt nfs defaults 0 0\n'
