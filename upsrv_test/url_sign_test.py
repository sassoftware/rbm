#
# Copyright (c) SAS Institute Inc.
#


import time
from testrunner import testcase
from testutils import mock
from webob import request

from upsrv import config
from upsrv import url_sign


class UrlSignTest(testcase.TestCase):

    def setUp(self):
        testcase.TestCase.setUp(self)
        self.cfg = config.UpsrvConfig()
        self.cfg.downloadSignatureExpiry = 3600
        self.cfg.downloadSignatureKey = ['default key']
        self.now = 1000000000.0
        mock.mock(time, 'time', self.now)

    def tearDown(self):
        mock.unmockAll()
        testcase.TestCase.tearDown(self)

    def _time(self, when):
        mock.mock(time, 'time', self.now + when)

    def _req(self, path):
        req = request.Request.blank(path)
        return req

    def testUrlSign(self):
        result = url_sign.sign_path(self.cfg, '/example')
        self.assertEqual(result, '/example?e=1000003600&s=4001ab09d49d0c585a06f243156a056ddde12cf4')

        self.cfg.downloadSignatureKey = []
        self.assertRaises(RuntimeError, url_sign.sign_path, self.cfg, '/example')

    def testUrlVerify(self):
        req = self._req('/example?e=1000003600&s=4001ab09d49d0c585a06f243156a056ddde12cf4')
        result = url_sign.verify_request(self.cfg, req)
        self.assertEqual(result, True)
        self.cfg.downloadSignatureKey = []
        self.assertRaises(RuntimeError, url_sign.verify_request, self.cfg, req)

    def testVerifyOldKey(self):
        self.cfg.downloadSignatureKey = ['b']
        path = url_sign.sign_path(self.cfg, '/example')
        self.cfg.downloadSignatureKey = ['a', 'b']
        self.assertNotEqual(url_sign.sign_path(self.cfg, '/example'), path)

        req = self._req(path)
        self.assertEqual(url_sign.verify_request(self.cfg, req), True)

    def testVerifyExpired(self):
        path = url_sign.sign_path(self.cfg, '/example')
        self._time(4000)
        req = self._req(path)
        result = url_sign.verify_request(self.cfg, req)
        self.assertEqual(result, False)

    def testVerifyBad(self):
        self.assertEqual(url_sign.verify_request(self.cfg, self._req('/example?e=1000003600')), False)
        self.assertEqual(url_sign.verify_request(self.cfg, self._req('/example?e=1000003600&s=')), False)
        path = url_sign.sign_path(self.cfg, '/example')
        path += '&e=2000000000'
        self._time(4000)
        self.assertEqual(url_sign.verify_request(self.cfg, self._req(path)), False)
