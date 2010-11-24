# Copyright (c) 2006-2008 rPath, Inc
# All rights reserved

import sys
import raa.web
from raa.modules.raawebplugin import rAAWebPlugin

from gettext import gettext as _
from conary.repository.netrepos.netserver import ServerConfig

from urlparse import urlparse
import traceback
import logging
log = logging.getLogger('rPath.rusmode')

class RUSMode(rAAWebPlugin):
    '''
        This plugin configures the mode of a rUS
    '''

    displayName = _("Proxy / Mirror Setup")

    cnrPath = "/srv/conary/repository.cnr"

    def _getReposCfg(self):
        cfg = ServerConfig()
        cfg.read(self.cnrPath)
        return cfg

    @raa.web.expose(template="rPath.rusmode.templates.rusmode")
    def index(self):
        cfg = self._getReposCfg()
        if cfg.repositoryDB == None:
            # py-2.6-ism
            # rbaHostname = getattr(urlparse(cfg.conaryProxy.get('http', '')), 
            #                       'hostname', '')
            rbaHostname = urlparse(cfg.conaryProxy.get('http', ''))[1] 
            return dict(mode='proxy', rbaHostname=rbaHostname)
        else:
            return dict(mode='mirror', rbaHostname='')

    @raa.web.expose(allow_json=True)
    def setMode(self, mode, rbaHostname):
        try:
            result = self.callBackend('setMode', mode, rbaHostname)
            if not result.has_key('errors'):
                self.wizardDone()
            if mode == "proxy":
                self.plugins['/reaentitlement/rEAEntitlement'].setPropertyValue('raa.hidden', True, data.RDT_BOOL)
                self.plugins['/mirrorusers/MirrorUsers'].setPropertyValue('raa.hidden', True, data.RDT_BOOL)
            else:
                self.plugins['/reaentitlement/rEAEntitlement'].setPropertyValue('raa.hidden', False, data.RDT_BOOL)
                self.plugins['/mirrorusers/MirrorUsers'].setPropertyValue('raa.hidden', False, data.RDT_BOOL)
            return result
        except Exception, e:
            log.error(traceback.format_exc(sys.exc_info()[2]))
            return dict(errors = [str(e)])

