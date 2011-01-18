#
# Copyright (C) 2006-2008, rPath, Inc.
# All rights reserved.
#

from raa.modules.raasrvplugin import rAASrvPlugin
from conary.lib import util as cny_util
import os
import subprocess
import pwd
import logging
log = logging.getLogger("rPath.reaentitlement")

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
            print >> fobj, "conaryProxy http http://%s" % rbaHostname
            print >> fobj, "conaryProxy https https://%s" % rbaHostname
            print >> fobj, "memCached localhost:11211"
            print >> fobj, "memCachedTimeout 600"

            fobj.commit()

            # Restart apache
            retcode = subprocess.call(['/sbin/service', 'httpd', 'graceful'])
            if retcode != 0:
                log.warning("Failed to restart httpd")
            return {'message': 'successfully configured proxy mode.\n\n'}

        elif mode == "mirror":
            # Write the new webserver config
            fobj = cny_util.AtomicFile(self.cfgFile)
            print >> fobj, "# Do not modify this file! Make a higher-numbered one"
            print >> fobj, "# and place your customizations there instead."
            print >> fobj, "repositoryDB    ", \
                "postgresql updateservice@localhost.localdomain:5439/updateservice"
            fobj.commit()

            # Initialize the database -- do this in a shell script,
            # because most of the code was already there...
            retcode = subprocess.call(['/srv/conary/bin/init-repos' ])
            if retcode != 0:
                log.error("Failed to initialize repository schema.")
                return {'errors': ["Failed to initialize repository schema."]}

            # Restart the webserver to apply the change
            retcode = subprocess.call(['/sbin/service', 'httpd', 'graceful'])

            return {'message': 'successfully configured mirror mode.\n\n'}
        else:
            return {'errors': [ 'not a valid mode: %s' % mode ]}
