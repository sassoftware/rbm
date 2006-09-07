import cherrypy
import os
import raatest

def setupCnr():
    """Write a fake repository.cnr file and return the filename"""
    import tempfile
    import os
    import sys

    fd, fn = tempfile.mkstemp()
    print >> sys.stderr, fn
    sys.stderr.flush()
    f = os.fdopen(fd, "w")

    f.write("serverName localhost")
    f.close()

    return fn

class webPluginTest(raatest.webTest):
    def __init__(
        self, module = None, init = True, preInit = None, preConst = None):

        def func(rt):
            cherrypy.root.servicecfg.pluginDirs = [os.path.join("..", "raaplugins")]
            if preInit:
                preInit(rt)

        return raatest.webTest.__init__(
            self, module=module, init=init, preInit=func, preConst=preConst)
