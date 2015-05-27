#!/bin/sh
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


/usr/sbin/tmpwatch 24 /srv/conary/tmp/
/usr/sbin/tmpwatch 336 /srv/conary/cscache/

if [ -e /srv/conary/proxycontents ] ; then
    /usr/sbin/tmpwatch 336 /srv/conary/proxycontents
fi

tmpwatch \
    --exclude=/srv/rbuilder/tmp/client_temp \
    --exclude=/srv/rbuilder/tmp/fastcgi_temp \
    --exclude=/srv/rbuilder/tmp/proxy_temp \
    --exclude=/srv/rbuilder/tmp/scgi_temp \
    --exclude=/srv/rbuilder/tmp/uwsgi_temp \
    24 /srv/rbuilder/tmp
