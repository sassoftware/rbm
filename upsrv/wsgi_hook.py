#
# Copyright (c) SAS Institute Inc.
#


import logging
import os
import sys
from conary.lib import log as cny_log
from conary.server import wsgi_hooks as cny_hook
from conary.repository.netrepos import netserver
from pyramid import httpexceptions as web_exc
from pyramid import response

from . import app
from . import rbm_rc


log = logging.getLogger(__name__)

CFG_PATH = '/srv/conary/repository.cnr'


class application(object):
    requestFactory = app.Request
    responseFactory = response.Response
    cfgPath = CFG_PATH

    iterable = None
    req = None
    start_response = None

    cny_cfg = None

    def __init__(self, environ, start_response):
        cny_log.setupLogging(consoleLevel=logging.INFO, consoleFormat='apache')
        # gunicorn likes to umask(0) when daemonizing, so put back something
        # reasonable if that's the case.
        oldUmask = os.umask(022)
        if oldUmask != 0:
            os.umask(oldUmask)
        self.start_response = start_response
        try:
            self.req = self.requestFactory(environ)
        except:
            log.exception("Error parsing request:")
            response = web_exc.HTTPBadRequest()
            self.iterable = response(environ, start_response)
            return

        try:
            response = self.handleRequest()
        except web_exc.HTTPException, exc:
            response = exc
        except:
            exc_info = sys.exc_info()
            response = self.handleError(exc_info)
        finally:
            logging.shutdown()
        if callable(response):
            self.iterable = response(environ, start_response)
        else:
            self.iterable = response

    def __iter__(self):
        return iter(self.iterable)

    def handleError(self, exc_info):
        # FIXME: mail tracebacks
        log.exception("Unhandled exception:")
        return web_exc.HTTPInternalServerError(explanation=
                "Something has gone terribly wrong. "
                "Check the webserver logs for details.")

    def handleRequest(self):
        if 'x-conary-servername' in self.req.headers:
            return self.handleConary()
        elem = self.req.path_info_peek()
        if elem == '':
            return web_exc.HTTPFound(location='/conary/browse')
        elif elem == 'conary':
            self.req.path_info_pop()
            return self.handleConary()
        elif elem == 'conaryrc':
            return self.handleRc()
        elif elem == 'downloads':
            return app.handle(self.req)
        else:
            return web_exc.HTTPNotFound()

    def getServerConfig(self):
        if self.cny_cfg is None:
            type(self).cny_cfg = netserver.ServerConfig()
            self.cny_cfg.read(self.cfgPath)
        return self.cny_cfg

    def handleConary(self):
        self.req.environ['conary.netrepos.mount_point'] = '/'
        handler = cny_hook.ConaryHandler(self.getServerConfig())
        return handler.handleRequest(self.req)

    def handleRc(self):
        return rbm_rc.rcfile(self.req, self.getServerConfig())
