#
# Copyright (c) SAS Institute Inc.
#

import hashlib
import getpass
import json
import os
import sys
from conary.command import HelpCommand
from conary.lib import mainhandler
from conary.lib import options
from conary.lib.command import AbstractCommand
from conary.repository import errors
from conary.repository.netrepos import netserver
from . import config


class Command(AbstractCommand):

    def addParameters(self, argDef):
        argDef[self.defaultGroup] = {
                'json': options.NO_PARAM,
                }

    def processConfigOptions(self, cfg, cfgMap, argSet):
        AbstractCommand.processConfigOptions(self, cfg, cfgMap, argSet)
        cfg.logFile = None
        self.cfg = cfg
        if cfg.repositoryDB:
            self.netRepos = netserver.NetworkRepositoryServer(cfg, 'localhost')
        else:
            self.netRepos = None

    def _prompt(self, argSet, arg, query):
        if arg in argSet:
            return argSet[arg]
        else:
            return raw_input(query)

    def _password(self, argSet):
        if 'password-stdin' in argSet:
            return sys.stdin.readline().rstrip('\r\n')
        elif 'password' in argSet:
            return argSet['password']
        while True:
            password = getpass.getpass("Password: ")
            password2 = getpass.getpass("Password (repeat): ")
            if password == password2:
                return password


class Script(mainhandler.MainHandler):
    commandList = [ HelpCommand ]
    abstractCommand = Command
    name = 'repo-tool'

    def configClass(self, readConfigFiles=True, ignoreErrors=None):
        cfg = config.UpsrvConfig()
        if readConfigFiles:
            cfg.read(config.CFG_PATH)
        return cfg


class UserList(Command):
    commands = ['user-list']

    def getUserList(self):
        nr = self.netRepos
        if not nr:
            return []
        cu = nr.db.cursor()
        ret = []
        cu.execute("SELECT username, salt, password FROM Users")
        for usr, salt, password in cu.fetchall():
            perm = 'other'
            roles = nr.auth.userAuth.getRolesByUser(usr)
            if len(roles) == 1:
                role = roles[0]
                for roleperm in nr.auth.iterPermsByRole(role):
                    # admin user
                    if nr.auth.roleIsAdmin(role) and \
                            roleperm == ('ALL', 'ALL', 1, 0):
                        perm = 'admin'
                        break
                    # mirror user
                    elif nr.auth.roleCanMirror(role) and \
                            roleperm == ('ALL', 'ALL', 1, 1):
                        perm = 'mirror'
                        break
                # anonymous user
                if role == 'anonymous':
                    perm = 'anonymous'
            # Complex roles (with more than one perm) are "Other"
            ret.append({
                'user-name' : usr,
                'permission' : perm,
                'salt': salt,
                'password': password,
                })
        return ret

    def runCommand(self, cfg, argSet, otherArgs):
        if 'json' in argSet:
            json.dump(self.getUserList(), sys.stdout)
            print
        else:
            if not self.cfg.repositoryDB:
                print "No users, repository is in proxy mode"
                return
            fmt = '%-10s %s'
            print fmt % ('Permission', 'Username')
            for x in self.getUserList():
                print fmt % (x['permission'], x['user-name'])
Script.commandList.append(UserList)


class UserAdd(Command):
    commands = ['user-add']

    def addParameters(self, argDef):
        super(UserAdd, self).addParameters(argDef)
        argDef['User Add Options'] = {
                'user-name': options.ONE_PARAM,
                'permission': options.ONE_PARAM,
                'password': options.ONE_PARAM,
                'password-stdin': options.NO_PARAM,
                'salt': options.ONE_PARAM,
                }

    def addUser(self, user, salt, password, permission):
        nr = self.netRepos
        if not nr:
            sys.exit("Repository is in proxy mode")
        if permission == 'mirror':
            write = True
            mirror = True
            admin = False
            remove = True
        elif permission == 'anonymous':
            write = False
            mirror = False
            admin = False
            remove = False
        elif permission == 'admin':
            write = True
            mirror = False
            admin = True
            remove = False
        else:
            sys.exit("Permission must be 'mirror', 'anonymous', or 'admin'")

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
        except:
            nr.db.rollback()
            raise

        # Now (maybe) create the user and add them to the role
        existed = False
        try:
            nr.auth.addUserByMD5(user, salt, password)
        except errors.UserAlreadyExists:
            nr.db.rollback()
            nr.auth.userAuth.changePassword(nr.db.cursor(), user, salt,
                    password)
            existed = True
        except:
            nr.db.rollback()
            raise

        nr.auth.setUserRoles(user, [role])
        return existed

    def runCommand(self, cfg, argSet, otherArgs):
        user_name = self._prompt(argSet, 'user-name', "User name: ")
        permission = self._prompt(argSet, 'permission',
                "Permission (mirror/admin/anonymous): ")
        password = self._password(argSet)
        if 'salt' in argSet:
            salt = argSet['salt'].decode('hex')
        else:
            salt = os.urandom(4)
            password = hashlib.md5(salt + password).hexdigest()
        existed = self.addUser(user_name, salt, password, permission)
        if 'json' in argSet:
            json.dump([True], sys.stdout)
            print
        else:
            if existed:
                print "Modified user '%s'" % user_name
            else:
                print "Created user '%s'" % user_name
Script.commandList.append(UserAdd)


class UserDelete(Command):
    commands = ['user-delete']

    def addParameters(self, argDef):
        super(UserDelete, self).addParameters(argDef)
        argDef['User Delete Options'] = {
                'user-name': options.ONE_PARAM,
                }

    def runCommand(self, cfg, argSet, otherArgs):
        user_name = self._prompt(argSet, 'user-name', "User name: ")
        if not self.netRepos:
            sys.exit("Repository is in proxy mode")
        self.netRepos.auth.deleteUserByName(user_name)
        if 'json' in argSet:
            json.dump([True], sys.stdout)
            print
        else:
            print "Deleted user '%s'" % user_name
Script.commandList.append(UserDelete)


if __name__ == '__main__':
    Script().main()
