import cherrypy
import os
import raatest

from conary import dbstore
from conary.server import schema

def setupCnr():
    """Write a fake repository.cnr file and return the filename"""
    import tempfile
    import os

    fd, fn = tempfile.mkstemp()
    f = os.fdopen(fd, "w")

    fd, dbFn = tempfile.mkstemp()
    os.close(fd)

    f.write("serverName localhost\n")
    f.write("repositoryDB sqlite %s" % dbFn)
    f.close()

    db = dbstore.connect(dbFn, "sqlite")
    schema.loadSchema(db)
    db.close()

    return fn

class webPluginTest(raatest.webTest):
    def __init__(
        self, module = None, init = True, preInit = None, preConst = None):

        def func(rt):
            cherrypy.root.servicecfg.pluginDirs = [os.path.join(os.path.dirname(__file__), '..', "raaplugins")]
            if preInit:
                preInit(rt)

        return raatest.webTest.__init__(
            self, module=module, init=init, preInit=func, preConst=preConst)
