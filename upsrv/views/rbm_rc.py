#
# Copyright (c) SAS Institute Inc.
#

from conary import dbstore
from pyramid.view import view_config


@view_config(route_name='conaryrc', request_method='GET')
def conaryrc(req):
    hostname = req.host
    cfg = req.cny_cfg
    if hostname.endswith(':80') or hostname.endswith(':443'):
        hostname = hostname.split(':')[0]

    # Lack of a repository indicates proxy mode (RBM-273)
    if cfg.repositoryDB == None:
        body = "proxyMap * conarys://%s\n" % hostname
    else:
        # Otherwise, we're in mirror mode
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

        body = ""
        for name in serverNames:
            body += "repositoryMap %s https://%s/conary/\n" % (name, hostname)

    req.response.content_type = 'text/plain'
    req.response.body = body
    return req.response
