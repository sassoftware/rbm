#
# Copyright (c) SAS Institute Inc.
#

from pyramid import authentication
from pyramid import httpexceptions as web_exc


authz = authentication.BasicAuthAuthenticationPolicy(None)


def authCheck(request, user):
    creds = authz._get_credentials(request)
    return creds == (user, request.cfg.password[user])


def authenticated(user):
    def decorate(func):
        def wrapper(request, *args, **kwargs):
            if not authCheck(request, user):
                return web_exc.HTTPForbidden()
            return func(request, *args, **kwargs)
        wrapper.func_name = func.func_name
        return wrapper
    return decorate
