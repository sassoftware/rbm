#
# Copyright (c) SAS Institute Inc.
#


import logging
import os
import sys
import webob
from conary.lib import log as cny_log
from conary.server import wsgi_hooks as cny_hook
from conary.repository.netrepos import netserver
from webob import exc as web_exc

from . import rbm_rc

log = logging.getLogger(__name__)

CFG_PATH = '/srv/conary/repository.cnr'


class application(object):
    requestFactory = webob.Request
    responseFactory = webob.Response
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
        try:
            self.req = self.requestFactory(environ)
        except:
            log.exception("Error parsing request:")
            response = web_exc.HTTPBadRequest()
            self.iterable = response(environ, start_response)
            return

        self.start_response = start_response
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
        if elem == 'conary':
            self.req.path_info_pop()
            return self.handleConary()
        elif elem == '':
            return web_exc.HTTPFound(location='/conary/browse')
        elif elem == 'conaryrc':
            return self.handleRc()
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
