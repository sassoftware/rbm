#
# Copyright (c) 2010 rPath, Inc.
#
# All rights reserved.
#

SUBDIRS = anaconda artwork conary-web ec2 postgresql rapa rmake3 taghandler nginx


all: default-all

install: default-install
	install -D -m0755 cleanup.sh $(DESTDIR)/etc/cron.daily/mirror
	install -D -m0755 group-script $(DESTDIR)/usr/share/upsrv/scripts/group-script
	install -D -m0644 repository.cnr $(DESTDIR)/srv/conary/repository.cnr
	install -D -m0644 entitlements.xml $(DESTDIR)/etc/conary/entitlements.xml
	install -D -m0644 conary.logrotate $(DESTDIR)/etc/logrotate.d/conary-repository
	install -D -m0644 firewall $(DESTDIR)/etc/sysconfig/iptables
	install -D -m0644 firewall6 $(DESTDIR)/etc/sysconfig/ip6tables
	install -D -m0644 gunicorn.conf $(DESTDIR)/etc/gunicorn.conf
	install -D -m0644 gunicorn.sysconfig $(DESTDIR)/etc/sysconfig/gunicorn

clean: default-clean


include $(TOP)/Make.rules
# vim: set sts=8 sw=8 noexpandtab :
