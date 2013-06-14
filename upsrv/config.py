#
# Copyright (c) SAS Institute Inc.
#

from conary.lib.cfgtypes import CfgList, CfgString
from conary.repository.netrepos import netserver

CFG_PATH = '/srv/conary/repository.cnr'


class UpsrvConfig(netserver.ServerConfig):

    downloadSignatureKey = CfgList(CfgString)

    @classmethod
    def load(cls):
        cfg = cls()
        cfg.read(CFG_PATH)
        return cfg
