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


class appengine_mirror (
    $proxy_upstream                 = 'UNSET',
    $web_enabled                    = 'false',
    $zone                           = 'Local rBuilder',
    $xmpp_host                      = 'UNSET',
    ) {

    service { 'gunicorn':
        ensure                      => running,
        enable                      => true,
    }

    file { '/srv/conary/config/50_repositorydb.cnr':
        ensure                      => file,
        notify                      => Service['gunicorn'],
        content => $proxy_upstream ? {
            'UNSET' => "\
# Managed by puppet, do not edit
repositoryDB psycopg2 updateservice@127.0.0.1:5439/updateservice
webEnabled $web_enabled
",
            default => "\
# Managed by puppet, do not edit
proxyContentsDir /srv/conary/proxycontents
conaryProxy http https://$proxy_upstream
conaryProxy https https://$proxy_upstream
"},
    }

    if $xmpp_host != 'UNSET' {
        service { 'rmake3-node':
            ensure                      => running,
            enable                      => true,
        }

        file { '/etc/rmake3/node.d/50_zone.conf':
            ensure                      => file,
            notify                      => Service['rmake3-node'],
            content => "\
zone $zone
xmppHost $xmpp_host
",
        }
    } else {
        service { 'rmake3-node':
            ensure                      => stopped,
            enable                      => false,
        }
    }
}
