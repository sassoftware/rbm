#
# Copyright (c) SAS Institute Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


from conary.lib.cfgtypes import CfgInt, CfgPath, CfgString
from conary.lib.cfgtypes import CfgList, CfgDict, CfgLineList
from conary.repository.netrepos import netserver

CFG_PATH = '/srv/conary/repository.cnr'


class UpsrvConfig(netserver.ServerConfig):

    downloadDB                  = (CfgString, 'postgresql://updateservice@127.0.0.1:6432/upsrv_app')
    downloadDir                 = (CfgPath, '/srv/conary/downloads')
    downloadSignatureKey        = CfgList(CfgString)
    downloadSignatureExpiry     = (CfgInt, 3600)

    password                    = CfgDict(CfgString)

    mirrorsInGroup              = CfgDict(CfgLineList(CfgString))
    countryUsesGroups           = CfgDict(CfgLineList(CfgString))
    defaultMirrorGroups         = CfgLineList(CfgString)

    @classmethod
    def load(cls):
        cfg = cls()
        cfg.read(CFG_PATH)
        return cfg
