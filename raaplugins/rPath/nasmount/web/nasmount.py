# Copyright (c) 2007 rPath, Inc
# All rights reserved

import random
from gettext import gettext as _

import raa.web
from raa.modules.raawebplugin import rAAWebPlugin

def marshallMessages(func):
    def wrapper(self, *args, **kwargs):
        res = func(self, *args, **kwargs)

        # strip messages stored in the class and pass them.
        messages = res.get('messages', [])
        messages.extend(self.messages)
        res['messages'] = messages
        self.messages = []

        # strip errors stored in the class and pass them.
        errors = res.get('errors', [])
        errors.extend(self.errors)
        res['errors'] = errors
        self.errors = []

        return res

    # masquerade wrapper as the original function.
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    return wrapper

class NasMount(rAAWebPlugin):
    '''
    Set up an NFS based mount point for repository contents
    '''
    displayName = _("Remote Contents Store")

    def __init__(self, *args, **kwargs):
        rAAWebPlugin.__init__(self, *args, **kwargs)
        self.messages = []
        self.errors = []

    def initPlugin(self):
        return

    @raa.web.expose(template="rPath.nasmount.templates.index")
    @marshallMessages
    def index(self, *args, **kwargs):
        server = remoteMount = ''

        mountPoint = '/srv/conary/contents'

        err, res = self.callBackend('getMount', mountPoint)
        if err:
            self.errors.append(res)
        else:
            server, remoteMount = res
        return {'server': server, 'remoteMount': remoteMount}

    def _setMount(self, server, remoteMount, mountPoint):
        res = self.callBackend('setMount', server, remoteMount, mountPoint)
        if res[0]:
            self.errors.append(res[1])
        else:
            self.messages.append('Sucessfully set remote contents store')

    @raa.web.expose(template="rPath.nasmount.templates.index")
    @marshallMessages
    def setMount(self, *args, **kwargs):
        for param in ('server', 'remoteMount'):
            if not kwargs.get(param):
                self.errors.append('Parameter Error: %s is missing' % \
                                       param)

        success = False
        if not self.errors:
            self._setMount(server = kwargs['server'],
                           remoteMount = kwargs['remoteMount'],
                           mountPoint = '/srv/conary/contents')

        if not self.errors:
            self.wizardDone()
        raise raa.web.raiseHttpRedirect('index', 302)

    @raa.web.expose(template="rPath.nasmount.templates.index")
    def cancel(self, *args, **kwargs):
        self.wizardDone()
        raise raa.web.raiseHttpRedirect('index', 302)
