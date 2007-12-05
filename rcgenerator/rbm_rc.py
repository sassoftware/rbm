#
# Copyright (c) 2007 rPath, Inc.
#
# All rights reserved
#

import os
import urlparse

from mod_python import apache

conaryrcPath = '/srv/www/html/conaryrc'

def handler(req):
    if req.uri != '/conaryrc':
        # We only handle conaryrc
        return apache.DECLINED

    if req.method.upper() != 'GET':
        return apache.HTTP_BAD_REQUEST

    if not os.path.isfile(conaryrcPath):
        return apache.HTTP_NOT_FOUND

    req.content_type = 'text/plain'

    f = open(conaryrcPath, 'r')
    for line in f:
        if line.startswith('repositoryMap '):
            _, serverName, url = line.strip().split(' ', 2)
            parsed = list(urlparse.urlparse(url))
            parsed[1] = req.hostname
            url = urlparse.urlunparse(parsed)
            req.write('repositoryMap %s %s\n' % (serverName, url))
        else:
            req.write(line)

    return apache.OK
