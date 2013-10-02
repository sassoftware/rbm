#
# Copyright (c) SAS Institute Inc.
#

import itertools
import StringIO
from conary import dbstore
from conary.deps import deps
from pyramid.view import view_config

REAL_IPS = deps.parseFlavor(
        '!reserved.site-local,!reserved.link-local,!reserved.loopback')


@view_config(route_name='conaryrc', request_method='GET')
def conaryrc(req):
    hostname = req.host
    cfg = req.cfg
    if cfg.mirrorsInGroup:
        return managedConaryrc(req)
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


def lookupCountry(req):
    for remote_ip in reversed(req.getForwardedFor()):
        flags = req.geoip.getFlags(remote_ip)
        if flags.satisfies(REAL_IPS):
            break
    else:
        return None
    for flag in list(flags.iterDepsByClass(deps.UseDependency))[0].flags:
        if flag.startswith('country.'):
            return flag[8:]
    return None


def managedConaryrc(req):
    body = StringIO.StringIO()

    cc = lookupCountry(req)
    print >> body, "# Detected country code %s" % cc

    # Choose a preferred mirror group
    groups = req.cfg.countryUsesGroups.get(cc)
    if not groups:
        groups = req.cfg.defaultMirrorGroups
    if not groups:
        groups = []

    def _emit(mirrors):
        # Stable sort order is best as the client will shuffle them
        # automatically.
        if mirrors:
            print >> body, "proxyMap *", ' '.join(sorted(mirrors))

    # Emit all mirrors in the preferred groups first.
    preferredMirrors = set()
    for group in groups:
        preferredMirrors.update(req.cfg.mirrorsInGroup.get(group, ()))
    _emit(preferredMirrors)

    otherMirrors = set(itertools.chain(*req.cfg.mirrorsInGroup.values()))
    otherMirrors -= preferredMirrors
    _emit(otherMirrors)

    req.response.content_type = 'text/plain'
    req.response.body = body.getvalue()
    return req.response
