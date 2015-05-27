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


import crypt
from pyramid import authentication
from pyramid import httpexceptions as web_exc


authz = authentication.BasicAuthAuthenticationPolicy(None)


def authCheck(request, user):
    creds = authz._get_credentials(request)
    password = request.cfg.password.get(user)
    return password and creds == (user, password)


def authenticated(user):
    def decorate(func):
        def wrapper(request, *args, **kwargs):
            if not authCheck(request, user):
                return web_exc.HTTPForbidden()
            return func(request, *args, **kwargs)
        wrapper.func_name = func.func_name
        return wrapper
    return decorate

class AuthCheckCallback(object):
    def __init__(self, authorizedUser):
        self.authorizedUser = authorizedUser

    def check(self, username, password, request):
        if username != self.authorizedUser:
            return None
        encryptedPw = request.cfg.password.get(username)
        if encryptedPw is None:
            return None
        if encryptedPw != crypt.crypt(password, encryptedPw):
            return None
        return username

def cryptauth(user):
    def decorate(func):
        def wrapper(request, *args, **kwargs):
            authObj = authentication.BasicAuthAuthenticationPolicy(
                    AuthCheckCallback(user).check)
            ok = authObj.authenticated_userid(request)
            if ok is None:
                return web_exc.HTTPForbidden()
            return func(request, *args, **kwargs)
        wrapper.func_name = func.func_name
        return wrapper
    return decorate
