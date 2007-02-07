#
# Copyright (c) 2006 rPath, Inc
# All rights reserved
#

from raa.modules.raawebplugin import rAAWebPlugin
import turbogears
import os

class DiskUsage(rAAWebPlugin):
    ''' 
	Displays Disk Usage
    '''
    displayName = _("View Disk Usage")
    tooltip     = _("Disk Usage")

    df_cmd = '/bin/df -ThP'

    @turbogears.expose(html="rPath.diskusage.disk")
    @turbogears.identity.require( turbogears.identity.not_anonymous() )
    def index(self):
        df = os.popen(self.df_cmd)
        data = []
        for line in df:
            splitLine = line.split()
            fstype = splitLine.pop(1)
            if fstype != 'none':
            	data.append(splitLine)
        df.close()
        return dict(data=data[1:])
