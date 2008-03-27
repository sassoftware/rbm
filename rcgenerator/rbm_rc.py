#
# Copyright (c) 2007 rPath, Inc.
#
# All rights reserved
#

import os
import urlparse

from mod_python import apache

def handler(req):
    if req.uri != '/conaryrc':
        # We only handle conaryrc
        return apache.DECLINED

    if req.method.upper() != 'GET':
        return apache.HTTP_BAD_REQUEST

    req.content_type = 'text/plain'
    req.write('repositoryMap * https://%s/conary/' % req.hostname)
    return apache.OK
