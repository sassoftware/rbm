#
# Copyright (c) SAS Institute Inc.
#


import crypt
import base64
import json
import datetime
import logging
from testrunner import testcase
from testutils import mock

from conary import conarycfg

from upsrv import config, app, db
from upsrv.views import records

class DatabaseTest(testcase.TestCaseWithWorkDir):
    def testMigrate(self):
        self.cfg = config.UpsrvConfig()
        self.cfg.downloadDB = "sqlite:///%s/%s" % (self.workDir, "upsrv.sqlite")
        self.wcfg = app.configure(self.cfg)
        maker = self.wcfg.registry.settings['db.sessionmaker']
        # New maker, without extensions, we don't need transaction
        # management
        makerArgs = maker.kw.copy()
        del makerArgs['extension']
        maker = maker.__class__(**makerArgs)
        conn = maker()
        conn.execute("""
            CREATE TABLE databaseversion (
                version                 integer         NOT NULL,
                minor                   integer         NOT NULL,
                PRIMARY KEY ( version, minor )
        )""")

        conn.execute("""
            INSERT INTO databaseversion (version, minor)
                 VALUES (0, 1)
            """)
        db.schema.updateSchema(conn)
        conn.commit()

        versions = [ x for x in conn.execute("select version, minor from databaseversion") ]
        self.assertEquals(versions, [ db.migrate.Version ])
        conn.close()


class RecordTest(testcase.TestCaseWithWorkDir):
    DefaultCreatedTime = '2013-12-11T10:09:08.080605'
    DefaultUuid = '00000000-0000-0000-0000-000000000000'
    DefaultSystemId = 'systemid0'
    DefaultEntitlements = [
            ('a', 'aaa'),
            ('*', 'bbb'),
            ]
    DefaultProducers = {
            'conary-system-model' : {
                'attributes' : {
                    'content-type' : 'text/plain',
                    'version' : '1',
                    },
                # The system model has some unversioned artifacts
                'data' : '''\
search "foo=cny.tv@ns:1/1-2-3"
install "group-university-appliance=university.cny.sas.com@sas:university-3p-staging/1-2-3[~!xen is: x86(i486,i586,i686) x86_64]"
install bar
update baz=/invalid.version.string@ns:1
''',
                },
            'system-information' : {
                'attributes' : {
                    'content-type' : 'application/json',
                    'version' : '1',
                    },
                'data' : {
                    'bootTime' : '2012-11-10T09:08:07',
                    'memory' : {
                        'MemFree' : '4142 kB',
                        'MemTotal' : '1020128 kB',
                        'SwapFree' : '4344 kB',
                        'SwapTotal' : '1048568 kB',
                        },
                    },
                },
            'string-encoded-json' : {
                'attributes' : {
                    'content-type' : 'application/json',
                    'version' : '1',
                    },
                'data' : json.dumps(dict(a=1, b=2)),
                },
            }
    Username = 'records-reader'
    Password = 'sikrit'

    def setUp(self):
        testcase.TestCaseWithWorkDir.setUp(self)
        # Delete all root handlers
        for handler in logging.root.handlers:
            logging.root.removeHandler(handler)
        logging.basicConfig(level=logging.DEBUG)
        self.logHandler = logging.root.handlers[0]
        mock.mockMethod(self.logHandler.handle)
        self.cfg = config.UpsrvConfig()
        self.cfg.downloadDB = "sqlite:///%s/%s" % (self.workDir, "upsrv.sqlite")
        salt = file("/dev/urandom").read(8).encode('hex')
        self.cfg.configLine('password %s %s' % (
            self.Username, crypt.crypt(self.Password, '$1$%s$' % salt)))

        self.wcfg = app.configure(self.cfg)

        maker = self.wcfg.registry.settings['db.sessionmaker']
        # New maker, without extensions, we don't need transaction
        # management
        makerArgs = maker.kw.copy()
        del makerArgs['extension']
        maker = maker.__class__(**makerArgs)
        conn = maker()
        db.schema.updateSchema(conn)
        conn.commit()

        self.conn = conn

        self.app = self.wcfg.make_wsgi_app()

        # Mock the conary config object
        self.conaryCfg = conarycfg.ConaryConfiguration(False)
        self.conaryCfg.root = "%s/%s" % (self.workDir, "__root__")
        mock.mock(conarycfg, 'ConaryConfiguration', self.conaryCfg)

    def tearDown(self):
        mock.unmockAll()
        testcase.TestCaseWithWorkDir.tearDown(self)
        for handler in logging.root.handlers:
            logging.root.removeHandler(handler)
        logging.root.setLevel(logging.WARNING)

    def _getLoggingCalls(self):
        logEntries = [ (x[0][0].name, x[0][0].msg, x[0][0].args)
                for x in self.logHandler.handle._mock.calls ]
        return logEntries

    def _resetLoggingCalls(self):
        del self.logHandler.handle._mock.calls[:]

    def _resetRecords(self):
        self.conn.execute("delete from records")
        self.conn.commit()

    def _req(self, path, method='GET', entitlements=None, headers=None, body=None):
        headers = headers or {}
        if entitlements:
            ents = " ".join("%s %s" % (x[0], base64.b64encode(x[1]))
                    for x in entitlements)
            headers['X-Conary-Entitlement'] = ents
        req = app.Request.blank(path, method=method, headers=headers or {},
                environ=dict(REMOTE_ADDR='10.11.12.13'))
        req.method = method
        req.headers.update(headers or {})
        req.body = body or ''
        req.cfg = self.cfg
        req._conaryClient = mock.MockObject()
        mock.mockMethod(req.getConaryClient, returnValue=req._conaryClient)
        return req

    @classmethod
    def _R(cls, uuid=None, system_id=None, producers=None,
            created_time=None, updated_time=None, **kwargs):
        uuid = uuid or cls.DefaultUuid
        system_id = system_id or cls.DefaultSystemId
        created_time = created_time or cls.DefaultCreatedTime
        updated_time = updated_time or '1980-01-01T00:00:00.000000'
        producers = producers or cls.DefaultProducers
        return dict(uuid=uuid, system_id=system_id,
                version=1, producers = producers,
                created_time=created_time, updated_time=updated_time, **kwargs)

    def testRecordCreate(self):
        url = '/registration/v1/records'
        req = self._req(url, method='POST')
        resp = self.app.invoke_subrequest(req, use_tweens=True)
        self.assertEquals(resp.status_code, 401)
        logEntries = self._getLoggingCalls()
        self.assertEquals(len(logEntries), 5)
        self.assertEquals(logEntries[3], ('upsrv.views.records', "Missing auth header `%s' from %s", ('X-Conary-Entitlement', '10.11.12.13')))
        self._resetLoggingCalls()

        # Include an entitlement, but no conary system model
        req = self._req(url, method='POST',
                entitlements=self.DefaultEntitlements,
                body=json.dumps(self._R(producers={
                    'system-information' : self.DefaultProducers['system-information']})))
        resp = self.app.invoke_subrequest(req, use_tweens=True)
        self.assertEquals(resp.status_code, 400)

        logEntries = self._getLoggingCalls()
        self.assertEquals(len(logEntries), 4)
        self.assertEquals(logEntries[1], ('upsrv.views.records', 'Missing system model from %s', ('10.11.12.13',)))
        self._resetLoggingCalls()

        # Correct record
        req = self._req(url, method='POST',
                entitlements=self.DefaultEntitlements,
                body=json.dumps(self._R()))
        resp = self.app.invoke_subrequest(req, use_tweens=True)
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.json_body['entitlement_valid'], True)
        self.assertEquals(resp.json_body['entitlements_json'],
                '[["a", "aaa"], ["*", "bbb"]]')

        now = datetime.datetime.utcnow()

        # Decode the json coming back
        record = json.loads(resp.body)
        self.assertEquals(record['uuid'], self.DefaultUuid)
        self.assertEquals(record['created_time'], self.DefaultCreatedTime)
        self.assertEquals(record['client_address'], '10.11.12.13')

        allRecords = records.records_view(req)
        self.assertEquals(allRecords.status_code, 403)

        # Let's add an auth header, with a bad username
        req.headers['Authorization'] = 'Basic %s' % base64.b64encode(
            '{username}:{password}'.format(username='faaaaake',
                password=self.Password))
        allRecords = records.records_view(req)
        self.assertEquals(allRecords.status_code, 403)

        # Let's add an auth header, with a good username and a bad password
        req.headers['Authorization'] = 'Basic %s' % base64.b64encode(
            '{username}:{password}'.format(username=self.Username,
                password='faaaaaaake'))
        allRecords = records.records_view(req)
        self.assertEquals(allRecords.status_code, 403)

        # Let's add an auth header, with a good username/password
        req.headers['Authorization'] = 'Basic %s' % base64.b64encode(
            '{username}:{password}'.format(username=self.Username,
                password=self.Password))
        # Make sure the record got persisted correctly
        allRecords = records.records_view(req)['records']
        self.assertEquals([ x['entitlement_valid'] for x in allRecords ],
                [ True ])
        self.assertEquals([ x['entitlements_json'] for x in allRecords ],
                [ '[["a", "aaa"], ["*", "bbb"]]' ])

        rec = allRecords[0]
        self.assertEquals(rec['uuid'], self.DefaultUuid)
        # Make sure updated_time got set by the server
        rectime = datetime.datetime.strptime(rec['updated_time'],
                "%Y-%m-%dT%H:%M:%S.%f")
        delta = now - rectime
        totalSeconds = 86400 * delta.days + delta.seconds
        self.assertTrue(0 <  totalSeconds)
        self.assertTrue(totalSeconds < 2)

        self.assertEquals(req.getConaryClient._mock.popCall(),
                ((), (('entitlements', ['aaa', 'bbb']),)))
        self.assertEquals(req.getConaryClient._mock.calls, [])

        # Remove all records
        self._resetLoggingCalls()
        self._resetRecords()

        # Same deal, but make findTroves raise an exception
        _calls = []
        _exc = records.repoerrors.TroveNotFound('blah')
        def fakeFindTroves(label, troves, *args, **kwargs):
            _calls.append((label, troves, args, kwargs))
            raise _exc
        req._conaryClient.repos._mock.set(findTroves=fakeFindTroves)
        resp = self.app.invoke_subrequest(req, use_tweens=True)
        self.assertEquals(resp.status_code, 200)
        self.assertEquals(resp.json_body['entitlement_valid'], False)
        self.assertEquals(resp.json_body['entitlements_json'],
                '[["a", "aaa"], ["*", "bbb"]]')

        logEntries = self._getLoggingCalls()
        self.assertEquals(len(logEntries), 5)
        self.assertEquals(logEntries[2],
                ('upsrv.views.records', '%s: bad entitlements %s for system model %s: %s',
                    ('10.11.12.13', [('a', 'aaa'), ('*', 'bbb')],
                        self.DefaultProducers['conary-system-model']['data'],
                        _exc)))

        self.assertEquals(len(_calls), 1)
        self.assertEquals([str(x) for x in _calls[0][1]],
                ['foo=cny.tv@ns:1/1-2-3', 'group-university-appliance=university.cny.sas.com@sas:university-3p-staging/1-2-3[~!xen is: x86(i486,i586,i686) x86_64]'])

        # Make sure the record got persisted correctly
        allRecords = records.records_view(req)['records']
        self.assertEquals([ x['entitlement_valid'] for x in allRecords ],
                [ False ])
        self.assertEquals([ x['entitlements_json'] for x in allRecords ],
                [ '[["a", "aaa"], ["*", "bbb"]]' ])

        # Remove all records
        self._resetLoggingCalls()
        self._resetRecords()
        # Same deal, but with a 1M provider payload
        content = '0123456789abcdef' * 64 * 1024
        req = self._req(url, method='POST',
                entitlements=self.DefaultEntitlements,
                body=json.dumps(self._R(producers={
                    'system-information' : content})))
        resp = self.app.invoke_subrequest(req, use_tweens=True)
        self.assertEquals(resp.status_code, 413)
        logEntries = self._getLoggingCalls()
        self.assertEquals(len(logEntries), 4)
        self.assertEquals(logEntries[2],
                ('upsrv.views.records', 'Request too large from %s: %s bytes',
                    ('10.11.12.13', 1048797)))

    def testDecodeEntitlements(self):
        tests = [
                ("", []),
                ("a", []),
                ("a YWFh", [('a', 'aaa')]),
                ("a YWFh *", [('a', 'aaa')]),
                ("a YWFh * YmJi", [('a', 'aaa'), ('*', 'bbb')]),
                ]
        for entString, expected in tests:
            self.assertEqual(records._decodeEntitlements(entString), expected)
