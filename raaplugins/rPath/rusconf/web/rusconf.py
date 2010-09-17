#
# Copyright (c) 2010 rPath, Inc.
#
# All rights reserved.
#

import cherrypy
import raa.web
from raa import authorization
from raa.modules.raawebplugin import rAAWebPlugin


class RusConf(rAAWebPlugin):
    '''
    Create or delete conary repository users
    '''
    displayName = "Internal update service configuration"

    roles = ['mirror']

    def __init__(self, *args, **kwargs):
        rAAWebPlugin.__init__(self, *args, **kwargs)
        raa.web.setConfigValue( {'rusconf.RusConf.hidden': True} )

    @raa.web.expose(allow_xmlrpc=True)
    @raa.web.require(authorization.PermissionPresent('mirror'))
    def pushConfiguration(self, confDict):
        if 'xmpp_host' not in confDict:
            remote_ip = cherrypy.request.remote.ip
            if remote_ip[:7] == '::ffff:':
                remote_ip = remote_ip[7:]
            confDict['xmpp_host'] = remote_ip
        return self.callBackend('pushConfiguration', confDict)
