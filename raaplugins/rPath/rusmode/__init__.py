#
# Copyright (c) rPath, Inc
#

import json
import subprocess

def runScript(method, *args):
    stdin = json.dumps(dict(method=method, args=args))
    proc = subprocess.Popen(['/usr/bin/python', '-mupsrv.tool'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, shell=False,
            )
    stdout, stderr = proc.communicate(stdin)
    if proc.returncode or not stdout:
        raise RuntimeError("upsrv script failed:\n%s\n" % stderr)
    result = json.loads(stdout)
    if isinstance(result, dict):
        newresult = {}
        for key, value in result.items():
            newresult[str(key)] = value
        return newresult
    else:
        return result
