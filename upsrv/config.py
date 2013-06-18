#
# Copyright (c) SAS Institute Inc.
#

from conary.lib.cfgtypes import CfgInt, CfgList, CfgPath, CfgString
from conary.repository.netrepos import netserver

CFG_PATH = '/srv/conary/repository.cnr'


class UpsrvConfig(netserver.ServerConfig):

    downloadDB                  = (CfgString, 'postgres://updateservice@127.0.0.1:6432/upsrv_app')
    downloadDir                 = (CfgPath, '/srv/conary/downloads')
    downloadSignatureKey        = CfgList(CfgString)
    downloadSignatureExpiry     = (CfgInt, 3600)
    downloadWriterPassword      = CfgString

    @classmethod
    def load(cls):
        cfg = cls()
        cfg.read(CFG_PATH)
        return cfg
