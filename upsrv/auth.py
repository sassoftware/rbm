#
# Copyright (c) SAS Institute Inc.
#

from pyramid import authentication
from pyramid import httpexceptions as web_exc


authz = authentication.BasicAuthAuthenticationPolicy(None)


def authCheck(request):
    if not request.cfg.downloadWriterPassword:
        return False
    creds = authz._get_credentials(request)
    return creds == ('dlwriter', request.cfg.downloadWriterPassword)


def authenticated(func):
    def wrapper(request, *args, **kwargs):
        if not authCheck(request):
            return web_exc.HTTPForbidden()
        return func(request, *args, **kwargs)
    return wrapper
