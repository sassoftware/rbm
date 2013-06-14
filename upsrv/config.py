#
# Copyright (c) SAS Institute Inc.
#

from conary.lib.cfgtypes import CfgInt, CfgList, CfgString
from conary.repository.netrepos import netserver

CFG_PATH = '/srv/conary/repository.cnr'


class UpsrvConfig(netserver.ServerConfig):

    downloadSignatureKey        = CfgList(CfgString)
    downloadSignatureExpiry     = (CfgInt, 3600)

    @classmethod
    def load(cls):
        cfg = cls()
        cfg.read(CFG_PATH)
        return cfg
