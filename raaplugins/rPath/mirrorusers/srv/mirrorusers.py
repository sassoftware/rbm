#
# Copyright (c) rPath, Inc.
#

import json
import subprocess
from raa.modules.raasrvplugin import rAASrvPlugin


class MirrorUsers(rAASrvPlugin):

    def _runScript(self, method, *args):
        stdin = json.dumps(dict(method=method, args=args))
        proc = subprocess.Popen(['/usr/bin/python', '-mupsrv_tool'],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=False)
        stdout, _ = proc.communicate(stdin)
        return dict((str(x), y) for (x, y) in json.loads(stdout).items())

    def getUserList(self, schedId, execId):
        return self._runScript('getUserList')

    def addUser(self, user, password, permission):
        return self._runScript('addUser', user, password, permission)

    def deleteUser(self, schedId, execId, user):
        return self._runScript('deleteUser', user)

    def changePassword(self, schedId, execId, user, newPass):
        return self._runScript('changePassword', user, newPass)
