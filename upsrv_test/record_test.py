#
# Copyright (c) SAS Institute Inc.
#


import json
import datetime
from testrunner import testcase
from testutils import mock

from upsrv import config, app, db
from upsrv.views import records

class RecordTest(testcase.TestCaseWithWorkDir):
    DefaultCreatedTime = '2013-12-11T10:09:08.080605'
    DefaultUuid = '00000000-0000-0000-0000-000000000000'
    DefaultSystemId = 'systemid0'
    DefaultProducers = {
            'conary-system-model' : {
                'attributes' : {
                    'content-type' : 'text/plain',
                    'version' : '1',
                    },
                'data' : 'install "group-university-appliance=university.cny.sas.com@sas:university-3p-staging/1-2-3[~!xen is: x86(i486,i586,i686) x86_64]"\n',
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

    def setUp(self):
        testcase.TestCaseWithWorkDir.setUp(self)
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
        db.migrate.createSchema(conn)
        conn.execute(app.sqlalchemy.sql.text("""\
            INSERT INTO databaseversion (version, minor)
                 VALUES (:version, :minor)
            """), params=dict(version=db.migrate.Version.major,
            minor=db.migrate.Version.minor))
        conn.commit()
        conn.close()

        self.app = self.wcfg.make_wsgi_app()
#        self.now = datetime.datetime(year=2020, month=12, day=24,
#                hour=15, minute=16, second=17)
#        mock.mock(datetime.datetime, 'now', self.now)

    def tearDown(self):
        mock.unmockAll()
        testcase.TestCaseWithWorkDir.tearDown(self)

    def _req(self, path, method='GET', headers=None, body=None):
        req = app.Request.blank(path, method=method, headers=headers or {},
                environ=dict(REMOTE_ADDR='10.11.12.13'))
        req.method = method
        req.headers.update(headers or {})
        req.body = body or ''
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

        req = self._req(url, method='POST',
                headers={'X-Conary-Entitlement' : 'aaa'},
                body=json.dumps(self._R()))
        resp = self.app.invoke_subrequest(req, use_tweens=True)
        self.assertEquals(resp.status_code, 200)

        now = datetime.datetime.now()

        # Decode the json coming back
        record = json.loads(resp.body)
        self.assertEquals(record['uuid'], self.DefaultUuid)
        self.assertEquals(record['created_time'], self.DefaultCreatedTime)
        self.assertEquals(record['client_address'], '10.11.12.13')

        allRecords = records.records_view(req)
        self.assertEquals(allRecords['count'], 1)
        rec = allRecords['records'][0]
        self.assertEquals(rec['uuid'], self.DefaultUuid)
        # Make sure updated_time got set by the server
        rectime = datetime.datetime.strptime(rec['updated_time'],
                "%Y-%m-%dT%H:%M:%S.%f")
        delta = now - rectime
        self.assertLess(0, delta.total_seconds())
        self.assertLess(delta.total_seconds(), 2)
