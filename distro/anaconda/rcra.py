#
# Copyright (c) 2010 rPath, Inc.
#
# All rights reserved.
#


from installclass import BaseInstallClass
from rhpl.translate import N_
from constants import CLEARPART_TYPE_ALL
import iutil

from autopart import getAutopartitionBoot, autoCreatePartitionRequests

class InstallClass(BaseInstallClass):
    hidden = 0
    
    id = "rcra"
    name = N_("r_cra")
    pixmap = "rpath-color-graphic-only.png"
    description = N_("rPath Conary Repository Appliance install type.")

    sortPriority = 100
    showLoginChoice = 1

    def setSteps(self, dispatch):
        BaseInstallClass.setSteps(self, dispatch);
        dispatch.skipStep("authentication")
        dispatch.skipStep("bootloader")
        dispatch.skipStep("package-selection")
        dispatch.skipStep("firewall")
        dispatch.skipStep("confirminstall")

    def setGroupSelection(self, grpset, intf):
        BaseInstallClass.__init__(self, grpset)

        grpset.unselectAll()
        grpset.selectGroup("everything")

    def setInstallData(self, id):
        BaseInstallClass.setInstallData(self, id)

        id.partitions.autoClearPartType = CLEARPART_TYPE_ALL
        id.partitions.autoClearPartDrives = []

        # (mntpt, fstype, minsize, maxsize, grow, format)
        autorequests = [ ("/var/log", None, 4096, 4096, 0, 1, 1),
                         ("/", None, 1, None, 1, 1, 1) ]

        bootreq = getAutopartitionBoot()
        if bootreq:
            autorequests.extend(bootreq)

        (minswap, maxswap) = iutil.swapSuggestion()
        autorequests.append((None, "swap", minswap, maxswap, 1, 1, 1))

        id.partitions.autoPartitionRequests = autoCreatePartitionRequests(autorequests)
        self.setFirewall(id, ports = ['22:tcp', '80:tcp', '161:tcp', '161:udp', '443:tcp', '8003:tcp'])
