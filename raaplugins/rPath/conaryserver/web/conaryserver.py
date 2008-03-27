# Copyright (c) 2006-2008 rPath, Inc
# All rights reserved

from raa.modules.raawebplugin import rAAWebPlugin
import raa.web
import turbogears

class ConaryServer(rAAWebPlugin):
    '''
        This plugin configures the conary repository hostnames.
    '''

    displayName = _("Update Repository Hostnames")

    roles = ['mirror']

    @raa.web.expose(allow_xmlrpc=True)
    @raa.web.require(turbogears.identity.has_permission('mirror'))
    def addServerName(self, servernames):
        '''
        DEPRECATED. We are using serverName * in the mirror configuration,
        so we don't need to explicitly set the serverNames anymore.
        '''
        return True

    @raa.web.expose(allow_xmlrpc=True)
    @raa.web.require(turbogears.identity.has_permission('mirror'))
    def delServerName(self, servername):
        '''
        DEPRECATED. We are using serverName * in the mirror configuration,
        so we don't need to explicitly set the serverNames anymore.
        '''
        return True
