#!/usr/bin/python
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


import datetime
import json
import optparse
import os
import sys
from conary import conaryclient, conarycfg, trovetup
from conary.lib import sha1helper
from conary.lib.http import opener


def main():
    parser = optparse.OptionParser(
            usage="usage: %prog http://mirror.host/downloads image.file image=trove[flavor]")
    parser.add_option('-n', '--name',
            help="Base name of the file. Default is to use the input file name.")
    parser.add_option('-m', '--metadata', action='append', default=[], metavar="KEY=VALUE",
            help="Attach arbitrary metadata to the image")
    options, args = parser.parse_args()
    if len(args) != 3:
        parser.error("Expected 3 arguments")
    baseurl, filepath, trovespec = args

    sha1 = sha1helper.sha1FileBin(filepath).encode('hex')
    fileobj = open(filepath, 'rb')
    st = os.fstat(fileobj.fileno())
    mtime = datetime.datetime.utcfromtimestamp(st.st_mtime)

    trove = findTrove(trovespec)

    doc = {
            'file_sha1': sha1,
            'file_basename': options.name or os.path.basename(filepath),
            'file_size': st.st_size,
            'file_modified': str(mtime) + ' UTC',
            'trove_name': str(trove.name),
            'trove_version': str(trove.version),
            'trove_flavor': str(trove.flavor),
            'trove_timestamp': trove.version.trailingRevision().timeStamp,
            'metadata': {},
            }
    for meta in options.metadata:
        key, value = meta.split('=', 1)
        doc['metadata'][key] = value
    doc = json.dumps(doc)

    o = Opener()
    print 'Creating image resource'
    o.open(baseurl + '/add', data=doc, method='POST',
            headers=[('Content-Type', 'application/json')])
    print 'Uploading image file'
    req = o.newRequest(baseurl + '/put/' + sha1, method='PUT',
            headers=[('Content-Type', 'application/octet-stream')])
    req.setData(fileobj, st.st_size)
    o.open(req)


class Opener(opener.URLOpener):

    def _handleError(self, request, response):
        if response.status < 300:
            return
        print response.status, response.reason
        print str(response.msg)
        print response.read()
        sys.exit(2)


def findTrove(trovespec):
    cfg = conarycfg.ConaryConfiguration(True)
    cli = conaryclient.ConaryClient(cfg)
    result = cli.repos.findTrove(None, trovetup.TroveSpec(trovespec))
    if len(result) > 1:
        print 'Multiple troves found, be more specific:'
        for tup in result:
            print '', tup
        sys.exit(1)
    return trovetup.TroveTuple(result[0])


main()
