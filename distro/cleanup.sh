#!/bin/sh
/usr/sbin/tmpwatch 24 /srv/conary/tmp/
/usr/sbin/tmpwatch 336 /srv/conary/cscache/

if [ -e /srv/conary/proxycontents ] ; then
    /usr/sbin/tmpwatch 336 /srv/conary/proxycontents
fi
