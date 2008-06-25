#
# Copyright (c) 2007 rPath, Inc.
#
# All rights reserved
#

import os
import urlparse
from conary import dbstore
from conary.repository.netrepos import netserver

from mod_python import apache

def handler(req):
    if req.uri != '/conaryrc':
        # We only handle conaryrc
        return apache.DECLINED

    if req.method.upper() != 'GET':
        return apache.HTTP_BAD_REQUEST

    cfg = netserver.ServerConfig()
    cfg.read('/srv/conary/repository.cnr')
    db = dbstore.connect(cfg.repositoryDB[1], driver = cfg.repositoryDB[0])
    cu = db.cursor()
    cu.execute("""SELECT LABEL FROM Labels WHERE EXISTS
                      ( SELECT labelId FROM LabelMap
                            JOIN Nodes USING(itemId, branchId)
                            JOIN Instances USING(itemId, versionId)
                        WHERE isPresent=1
                            AND LabelMap.labelId = Labels.labelId )""")
    serverNames = set()
    for label, in cu:
        if '@' not in label:
            continue
        name = label.split('@', 1)[0]
        serverNames.add(name)

    req.content_type = 'text/plain'

    for name in serverNames:
        req.write('repositoryMap %s https://%s/conary/\n' % (name, req.hostname))

    return apache.OK
