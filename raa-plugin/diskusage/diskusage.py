# Copyright (c) 2006 rPath, Inc
# All rights reserved

from raa.modules.raaplugin import rAAWebPlugin
import turbogears
import os

class DiskUsage(rAAWebPlugin):
    ''' 
	Displays Disk Usage
    '''
    displayName = _("View Disk Usage")
    tooltip     = _("Disk Usage")

    df_cmd = '/bin/df -h'

    @turbogears.expose(html="raa.modules.diskusage.disk")
    @turbogears.identity.require( turbogears.identity.not_anonymous() )
    def index(self):
        df = os.popen(self.df_cmd)
        data = []
        for line in df:
            data.append(line.split())
        df.close()
        return dict(data=data[1:])
