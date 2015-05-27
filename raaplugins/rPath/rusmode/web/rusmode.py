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


import sys
import raa.web
from raa.modules.raawebplugin import rAAWebPlugin
from raa.db import data
from .. import runScript

from gettext import gettext as _

import traceback
import logging
log = logging.getLogger('rPath.rusmode')

class RUSMode(rAAWebPlugin):
    '''
        This plugin configures the mode of a rUS
    '''

    displayName = _("Proxy / Mirror Setup")

    cnrPath = "/srv/conary/repository.cnr"

    @raa.web.expose(template="rPath.rusmode.templates.rusmode")
    def index(self):
        return runScript('getMode')

    @raa.web.expose(allow_json=True)
    def setMode(self, mode, rbaHostname):
        try:
            result = self.callBackend('setMode', mode, rbaHostname)
            if not result.has_key('errors'):
                self.wizardDone()
            if mode == "proxy":
                self.plugins['/mirrorusers/MirrorUsers'].setPropertyValue('raa.hidden', True, data.RDT_BOOL)
            else:
                self.plugins['/mirrorusers/MirrorUsers'].setPropertyValue('raa.hidden', False, data.RDT_BOOL)
            return result
        except Exception, e:
            log.error(traceback.format_exc(sys.exc_info()[2]))
            return dict(errors = [str(e)])
