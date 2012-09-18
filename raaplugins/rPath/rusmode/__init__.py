#
# Copyright (c) rPath, Inc
#

import json
import subprocess

def runScript(method, *args):
    stdin = json.dumps(dict(method=method, args=args))
    proc = subprocess.Popen(['/usr/bin/python', '-mupsrv_tool'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=False)
    stdout, _ = proc.communicate(stdin)
    return dict((str(x), y) for (x, y) in json.loads(stdout).items())
