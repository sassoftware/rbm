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
