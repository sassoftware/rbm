#
# Copyright (c) SAS Institute Inc.
#

import pyramid_tm
import sqlalchemy
from conary import conarycfg
from conary import conaryclient
from conary.repository.netrepos.auth_tokens import AuthToken
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
    def db(self):
        maker = self.registry.settings['db.sessionmaker']
        db = maker()
        schema.checkVersion(db)
        return db

    def getConaryClient(self, entitlements=()):
        cfg = conarycfg.ConaryConfiguration(False)
        cfg.configLine('includeConfigFile http://localhost/conaryrc')
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
    cfg.add_route('downloads_index',    '/downloads')
    cfg.add_route('downloads_add',      '/downloads/add')
    cfg.add_route('downloads_get',      '/downloads/get/{sha1}')
    cfg.add_route('downloads_put',      '/downloads/put/{sha1}')
    cfg.add_route('downloads_customer', '/customers/{cust_id}/downloads')
    cfg.add_route('cust_ents',          '/customers/{cust_id}/entitlements')
    cfg.add_route('cust_ent_put',       '/customer_entitlements')
    # Views
    cfg.scan(package='upsrv.views')
    return cfg


def handle(request):
    cfg = configure(ucfg=request.cfg)
    app = cfg.make_wsgi_app()
    return app.invoke_subrequest(request, use_tweens=True)
