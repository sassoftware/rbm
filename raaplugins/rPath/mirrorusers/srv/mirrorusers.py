#
# Copyright (c) rPath, Inc.
#

from raa.modules.raasrvplugin import rAASrvPlugin
from ...rusmode import runScript


class MirrorUsers(rAASrvPlugin):

    def getUserList(self, schedId, execId):
        return runScript('getUserList')

    def addUser(self, schedId, execId, user, password, permission):
        return runScript('addUser', user, password, permission)

    def deleteUser(self, schedId, execId, user):
        return runScript('deleteUser', user)

    def changePassword(self, schedId, execId, user, newPass):
        return runScript('changePassword', user, newPass)
