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


import grp
import logging
import os
import subprocess
from conary.lib import util as cny_util
from raa.modules.raasrvplugin import rAASrvPlugin

log = logging.getLogger('raa.service')


class RusConf(rAASrvPlugin):

    x509_path = '/etc/pki/tls/certs/localhost.crt'
    pkey_path = '/etc/pki/tls/private/localhost.key'
    alt_path = '/srv/rbuilder/pki/httpd.pem'

    rmake_cfg = '/etc/rmake3/node.d/25_runtime.conf'
    rmake_cred = '/srv/rmake3/worker.ident'

    def pushConfiguration(self, schedId, execId, data):
        try:
            ret = {}

            # Write httpd certificates
            self._deploy(data['x509_pem'], self.x509_path, 'apache')
            self._deploy(data['pkey_pem'], self.pkey_path, 'apache')

            # Write rpath-repeater certificates
            self._deploy(data['x509_pem'] + data['pkey_pem'], self.alt_path,
                    'root')

            # Configure rmake-node target host for XMPP
            ret.update(self._configureRmake(data))

            # Restart nginx after swapping out SSL certs.
            retcode = subprocess.call(['/sbin/service', 'nginx', 'restart'])

            return ret

        except Exception, err:
            log.exception("Unhandled exception while configuring "
                    "update service:")
            return {'errors': [str(err)]}

    def _deploy(self, data, path, group):
        try:
            groupid = grp.getgrnam(group).gr_gid
        except KeyError:
            log.error("Not deploying certificate %s: group %s not found.",
                    path, group)
            return

        if not os.path.isdir(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        fobj = cny_util.AtomicFile(path, chmod=0640)
        os.chown(fobj.name, 0, groupid)
        fobj.write(data)
        fobj.commit()
        log.info("Deployed certificate to %s", path)

    def _configureRmake(self, data):
        user = os.urandom(16).encode('hex')
        password = os.urandom(16).encode('hex')
        host = 'rbuilder.rpath'
        resource = 'rmake'
        jid = '%s@%s/%s' % (user, host, resource)

        # Point rmake at the upstream rBuilder.
        fobj = cny_util.AtomicFile(self.rmake_cfg)
        print >> fobj, "# Do not modify this file! Make a higher-numbered one"
        print >> fobj, "# and place your customizations there instead."
        print >> fobj, "xmppHost", data['xmpp_host']
        fobj.commit()

        # Write the credentials file out by hand so we know the account name
        # ahead of time. rmake will register them automatically on startup.
        fobj = cny_util.AtomicFile(self.rmake_cred, chmod=0600)
        print >> fobj, host, user, password
        fobj.commit()

        ret = os.system("/sbin/service rmake3-node restart")
        if ret:
            log.error("Error restarting rmake3-node: returned %s", ret)
            return {'errors': ['Failed to start rMake service.']}

        return {'jid': jid}
