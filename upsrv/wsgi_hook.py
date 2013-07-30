#
# Copyright (c) SAS Institute Inc.
#


import logging
import os
import sys
from conary.lib import log as cny_log
from conary.server import wsgi_hooks as cny_hook
from pyramid import httpexceptions as web_exc
from pyramid import response

from . import app
from . import config


log = logging.getLogger(__name__)


class application(object):
    requestFactory = app.Request
    responseFactory = response.Response

    iterable = None
    req = None
    start_response = None

    cfg = None

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

        if self.cfg is None:
            type(self).cfg = config.UpsrvConfig.load()
        self.req.cfg = self.cfg

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
        else:
            return app.handle(self.req)

    def handleConary(self):
        self.req.environ['conary.netrepos.mount_point'] = '/'
        handler = cny_hook.ConaryHandler(self.cfg)
        return handler.handleRequest(self.req)
