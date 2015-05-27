#
# Copyright (c) SAS Institute Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import pyramid_tm
import sqlalchemy
from conary import conarycfg
from conary import conaryclient
from conary.repository import errors as cny_errors
from conary.repository.netrepos.auth_tokens import AuthToken
from conary.repository.netrepos import geoip
from conary.server.wsgi_hooks import ConaryHandler
from pyramid import config
from pyramid import request
from pyramid.decorator import reify
from sqlalchemy.pool import NullPool

from . import render
from .db import models
from .db import schema


class Request(request.Request):

    @reify
    def geoip(self):
        return geoip.GeoIPLookup(self.cfg.geoIpFiles)

    @reify
    def db(self):
        maker = self.registry.settings['db.sessionmaker']
        db = maker()
        schema.checkVersion(db)
        return db

    def getConaryClient(self, entitlements=()):
        cfg = conarycfg.ConaryConfiguration(False)
        cfg.configLine('proxyMap * conarys://localhost/conary/')
        for key in entitlements:
            cfg.entitlement.addEntitlement('*', key)
        cli = conaryclient.ConaryClient(cfg)
        self.addHeaders(cli)
        return cli

    def getForwardedFor(self):
        authToken = AuthToken()
        ConaryHandler.setRemoteIp(authToken, request=self)
        return authToken.forwarded_for + [authToken.remote_ip]

    def addHeaders(self, cli):
        cache = cli.repos.c
        forwarded_for = self.getForwardedFor()
        old_factory = cache.TransportFactory
        def TransportFactory(*args, **kwargs):
            transport = old_factory(*args, **kwargs)
            if forwarded_for:
                transport.addExtraHeaders({
                    'x-forwarded-for': ', '.join(forwarded_for)})
            return transport
        cache.TransportFactory = TransportFactory

    def filterFiles(self, files, cust_id=None):
        if cust_id is not None:
            entitlements = self.db.query(models.CustomerEntitlement,
                    ).filter_by(cust_id=cust_id
                    ).all()
            entitlements = [x.entitlement.encode('ascii') for x in entitlements]
        else:
            entitlements = []
        repos = self.getConaryClient(entitlements).repos
        try:
            has_files = repos.hasTroves(x.trove_tup for x in files)
            return [x for x in files if has_files[x.trove_tup]]
        except cny_errors.InsufficientPermission:
            return []


def configure(ucfg):
    dburl = ucfg.downloadDB
    engine = sqlalchemy.create_engine(dburl, poolclass=NullPool)
    maker = models.initialize_sql(engine, use_tm=True)
    settings = {
            'db.sessionmaker': maker,
            }

    # Configuration
    cfg = config.Configurator(settings=settings)
    cfg.add_renderer('json', render.json_render_factory)
    cfg.include(pyramid_tm)
    # Routes
    cfg.add_route('conaryrc',           '/conaryrc')
    cfg.add_route('images_index',       '/images')
    cfg.add_route('image',              '/images/by_id/{sha1}')
    cfg.add_route('image_content',      '/images/by_id/{sha1}/content')
    cfg.add_route('customer_content',   '/images/by_id/{sha1}/content/{cust_id}')
    cfg.add_route('customer_images',    '/images/by_customer/{cust_id}')
    cfg.add_route('cust_ents',          '/customers/{cust_id}/entitlements')
    cfg.add_route('cust_ent_put',       '/customer_entitlements')
    # Registration
    cfg.add_route('records',            '/registration/v1/records')
    # Views
    cfg.scan(package='upsrv.views')
    return cfg


def handle(request):
    cfg = configure(ucfg=request.cfg)
    app = cfg.make_wsgi_app()
    return app.invoke_subrequest(request, use_tweens=True)
