#
# Copyright (c) 2010 rPath, Inc.
#
# All rights reserved.
#

import sys
sys.path.insert(0, '/usr/lib/anaconda/installclasses')

import iutil
import partRequests
from constants import BL_EXTLINUX
from fsset import fileSystemTypeGet
from pykickstart.constants import CLEARPART_TYPE_ALL
from rhpl.translate import N_
from rpathapp import InstallClass as BaseInstallClass


class InstallClass(BaseInstallClass):
    hidden = 0

    id = "rcra"
    name = N_("r_cra")
    pixmap = "rpath-color-graphic-only.png"
    description = N_("rPath Update Service install type.")

    sortPriority = 100
    showLoginChoice = 1

    def setSteps(self, anaconda):
        BaseInstallClass.setSteps(self, anaconda);
        dispatch = anaconda.dispatch
        dispatch.skipStep("authentication")
        dispatch.skipStep("bootloader", permanent=1)
        dispatch.skipStep("package-selection")
        dispatch.skipStep("firewall")
        dispatch.skipStep("confirminstall")
        #dispatch.skipStep("accounts")
        #dispatch.skipStep("complete")

    def setInstallData(self, anaconda):
        BaseInstallClass.setInstallData(self, anaconda)
        anaconda.id.partitions.autoClearPartType = CLEARPART_TYPE_ALL
        anaconda.id.bootloader.setBootLoader(BL_EXTLINUX)

        #anaconda.id.rootPassword['password'] = ''
        #anaconda.id.rootPassword['isCrypted'] = True

    def setDefaultPartitioning(self, partitions, clear=CLEARPART_TYPE_ALL,
            doClear=1):
        partitions.autoClearPartDrives = None
        partitions.autoPartitionRequests = requests = []
        ext3 = fileSystemTypeGet('ext3')

        # /boot - 100 MiB
        requests.append(partRequests.PartitionSpec(
            fstype=ext3, size=100, mountpoint='/boot', primary=1, format=1))
        # LVM
        requests.append(partRequests.PartitionSpec(
            fstype=fileSystemTypeGet('physical volume (LVM)'),
            size=4096, grow=1, format=1, multidrive=1))
        requests.append(partRequests.VolumeGroupRequestSpec(
            fstype=fileSystemTypeGet('volume group (LVM)'),
            vgname='vg00', physvols=[], format=1))
        # /
        requests.append(partRequests.LogicalVolumeRequestSpec(
            fstype=ext3, volgroup='vg00', lvname='root', mountpoint='/',
            size=4096, format=1, grow=1))
        # /var/log - 4 GiB
        requests.append(partRequests.LogicalVolumeRequestSpec(
            fstype=ext3, volgroup='vg00', lvname='logs', mountpoint='/var/logs',
            size=4096, format=1))
        # swap - as recommended
        minswap, maxswap = iutil.swapSuggestion()
        requests.append(partRequests.LogicalVolumeRequestSpec(
            fstype=fileSystemTypeGet('swap'),
            volgroup='vg00', lvname='swap',
            size=minswap, maxSizeMB=maxswap, format=1))
