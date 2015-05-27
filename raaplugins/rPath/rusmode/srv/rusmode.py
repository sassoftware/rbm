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


from raa.modules.raasrvplugin import rAASrvPlugin
from conary.lib import util as cny_util
import os
import subprocess
import pwd
import logging
log = logging.getLogger("rPath.rusmode")

class RUSMode(rAASrvPlugin):
    """
    Configure mirror/proxy mode
    """

    cfgFile = '/srv/conary/config/50_repositorydb.cnr'
    proxyDir = '/srv/conary/proxycontents'

    def setMode(self, schedId, execId, mode, rbaHostname):
        if mode == "proxy":
            # Create the proxy contents directory
            cny_util.mkdirChain(self.proxyDir)
            apache = pwd.getpwnam('apache')
            os.chown(self.proxyDir, apache.pw_uid, apache.pw_gid)

            # Write the new webserver config    
            fobj = cny_util.AtomicFile(self.cfgFile)
            print >> fobj, "# Do not modify this file! Make a higher-numbered one"
            print >> fobj, "# and place your customizations there instead."
            print >> fobj, "proxyContentsDir %s" % self.proxyDir
            print >> fobj, "conaryProxy http https://%s" % rbaHostname
            print >> fobj, "conaryProxy https https://%s" % rbaHostname

            fobj.commit()

            # Restart apache
            retcode = subprocess.call(['/sbin/service', 'gunicorn', 'reload'])
            if retcode != 0:
                log.warning("Failed to restart gunicorn")
            return {'message': 'successfully configured proxy mode.\n\n'}

        elif mode == "mirror":
            # Write the new webserver config
            fobj = cny_util.AtomicFile(self.cfgFile)
            print >> fobj, "# Do not modify this file! Make a higher-numbered one"
            print >> fobj, "# and place your customizations there instead."
            print >> fobj, "repositoryDB    ", \
                "psycopg2 updateservice@localhost.localdomain:5439/updateservice"
            fobj.commit()

            # Initialize the database -- do this in a shell script,
            # because most of the code was already there...
            retcode = subprocess.call(['/srv/conary/bin/init-repos' ])
            if retcode != 0:
                log.error("Failed to initialize repository schema.")
                return {'errors': ["Failed to initialize repository schema."]}

            # Restart the webserver to apply the change
            retcode = subprocess.call(['/sbin/service', 'gunicorn', 'reload'])

            return {'message': 'successfully configured mirror mode.\n\n'}
        else:
            return {'errors': [ 'not a valid mode: %s' % mode ]}
