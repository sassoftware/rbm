#!/bin/sh
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
