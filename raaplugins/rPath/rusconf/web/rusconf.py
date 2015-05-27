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
