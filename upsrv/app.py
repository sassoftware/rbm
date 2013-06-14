#
# Copyright (c) SAS Institute Inc.
#

import pyramid_tm
import sqlalchemy
from conary import conarycfg
from conary import conaryclient
from pyramid import config
from pyramid import request
from pyramid.decorator import reify

from . import models
from . import render


class Request(request.Request):

    @reify
    def db(self):
        maker = self.registry.settings['db.sessionmaker']
        return maker()

    def getConaryClient(self, entitlement=None):
        cfg = conarycfg.ConaryConfiguration(False)
        cfg.configLine('includeConfigFile http://localhost/conaryrc')
        if entitlement:
            cfg.entitlement.addEntitlement('*', entitlement)
        return conaryclient.ConaryClient(cfg)


def configure():
    engine = sqlalchemy.create_engine('postgresql://updateservice@localhost:6432/upsrv_app')
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
    cfg.add_route('downloads_get',      '/downloads/get/{sha1}')
    # Views
    cfg.scan(package='upsrv.views')
    return cfg


def handle(request):
    cfg = configure()
    app = cfg.make_wsgi_app()
    return app.invoke_subrequest(request, use_tweens=True)
