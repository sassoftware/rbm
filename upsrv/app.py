#
# Copyright (c) SAS Institute Inc.
#

import pyramid_tm
import sqlalchemy
from conary import conarycfg
from conary import conaryclient
from conary.web.webauth import parseEntitlement
from pyramid import config
from pyramid import request
from pyramid.decorator import reify

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

    def getConaryClient(self):
        cfg = conarycfg.ConaryConfiguration(False)
        cfg.configLine('includeConfigFile http://localhost/conaryrc')
        entList = parseEntitlement(self.headers.get('x-conary-entitlement', ''))
        for _, key in entList:
            cfg.entitlement.addEntitlement('*', key)
        return conaryclient.ConaryClient(cfg)


def configure(ucfg):
    dburl = ucfg.downloadDB
    engine = sqlalchemy.create_engine(dburl)
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
    cfg.add_route('cust_ents',          '/customers/{cust_id}/entitlements')
    # Views
    cfg.scan(package='upsrv.views')
    return cfg


def handle(request):
    cfg = configure(ucfg=request.cfg)
    app = cfg.make_wsgi_app()
    return app.invoke_subrequest(request, use_tweens=True)
