#!/usr/bin/python
#
# Copyright (c) rPath, Inc.
#

import json
import sys
from urlparse import urlparse
from conary.dbstore import sqlerrors
from conary.repository.netrepos.netserver import ServerConfig
from conary.repository.netrepos.netserver import NetworkRepositoryServer
from conary.repository import errors

CFG_PATH = '/srv/conary/repository.cnr'

class UpsrvTool(object):

    def __init__(self, cfgPath=CFG_PATH):
        self.cfgPath = cfgPath
        self.cfg = ServerConfig()
        self.cfg.read(cfgPath)

    def _getRepos(self):
        if self.cfg.repositoryDB:
            try:
                return NetworkRepositoryServer(self.cfg, 'localhost')
            except sqlerrors.SchemaVersionError:
                return None
        return None

    def getUserList(self):
        nr = self._getRepos()
        if not nr:
            return []
        users = nr.auth.userAuth.getUserList()
        ret = []
        for usr in users:
            perm = 'Other'
            roles = nr.auth.userAuth.getRolesByUser(usr)
            if len(roles) == 1:
                role = roles[0]
                for roleperm in nr.auth.iterPermsByRole(role):
                    # admin user
                    if nr.auth.roleIsAdmin(role) and \
                            roleperm == ('ALL', 'ALL', 1, 0):
                        perm = 'Admin'
                        break
                    # mirror user
                    elif nr.auth.roleCanMirror(role) and \
                            roleperm == ('ALL', 'ALL', 1, 1):
                        perm = 'Mirroring'
                        break
                # anonymous user
                if role == 'anonymous':
                    if usr == 'anonymous':
                        perm = 'Anonymous'
                    else:
                        perm = 'Read-Only'
            # Complex roles (with more than one perm) are "Other"
            ret.append({'user' : usr, 'permission' : perm})
        return ret

    def addUser(self, user, password, permission):
        nr = self._getRepos()
        if not nr:
            return dict(error='ProxyMode')
        if permission == 'Mirror':
            write = True
            mirror = True
            admin = False
            remove = True
        elif permission == 'Anonymous':
            write = False
            mirror = False
            admin = False
            remove = False
        elif permission == 'Admin':
            write = True
            mirror = False
            admin = True
            remove = False

        # First create a role for the desired permission
        role = permission.lower()
        try:
            nr.auth.addRole(role)
            nr.auth.addAcl(role, None, None, write=write, remove=remove)
            nr.auth.setAdmin(role, admin)
            nr.auth.setMirror(role, mirror)
        except errors.RoleAlreadyExists:
            # Not an error, but roll back the DB anyway
            nr.db.rollback()
        except errors.InvalidName:
            nr.db.rollback()
            return dict(error='InvalidName')
        except:
            nr.db.rollback()
            raise

        # Now (maybe) create the user and add them to the role
        try:
            nr.auth.addUser(user, password)
            nr.auth.addRoleMember(role, user)
        except errors.UserAlreadyExists:
            nr.db.rollback()
            return dict(error='UserAlreadyExists')
        except errors.InvalidName:
            nr.db.rollback()
            return dict(error='InvalidName')
        except:
            nr.db.rollback()
            raise

        return {}

    def deleteUser(self, user):
        nr = self._getRepos()
        if not nr:
            return False
        try:
            nr.auth.deleteUserByName(user)
        except:
            nr.db.rollback()
            raise

        return True

    def changePassword(self, schedId, execId, user, newPass):
        nr = self._getRepos()
        if not nr:
            return dict(errors=["Password change failed"])
        try:
            nr.auth.changePassword(user, newPass)
        except Exception, e:
            nr.db.rollback()
            return dict(errors=["Password change failed: %s" % str(e)])

        return dict(message="Password changed for %s" % user)

    def getMode(self):
        if self.cfg.repositoryDB:
            mode = 'mirror'
            rbaHostname = ''
        else:
            mode = 'proxy'
            rbaHostname = urlparse(self.cfg.conaryProxy.get('http', ''))[1]
        return dict(mode=mode, rbaHostname=rbaHostname)


def main():
    tool = UpsrvTool()
    dat_in = json.loads(sys.stdin.read())
    method = dat_in['method']
    if method.startswith('_') or not hasattr(tool, method):
        sys.exit("wrong method")
    args = dat_in['args']
    result = getattr(tool, method)(*args)
    sys.stdout.write(json.dumps(result))


if __name__ == '__main__':
    main()
