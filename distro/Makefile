#
# Copyright (c) 2010 rPath, Inc.
#
# All rights reserved.
#

SUBDIRS = anaconda conary-web ec2 httpd postgresql rapa taghandler


all: default-all

install: default-install
	install -D -m0644 repository.cnr $(DESTDIR)/srv/conary/repository.cnr
	install -D -m0644 ntpd.chkconfig $(DESTDIR)/etc/chkconfig.d/ntpd
	install -D -m0755 updateservice.init $(DESTDIR)/etc/init.d/updateservice
	install -D -m0755 cleanup.sh $(DESTDIR)/etc/cron.daily/mirror
	install -D -m0644 firewall.upsrv $(DESTDIR)/etc/firewall
	install -D -m0644 entitlements.xml $(DESTDIR)/etc/conary/entitlements.xml

clean: default-clean


include $(TOP)/Make.rules
# vim: set sts=8 sw=8 noexpandtab :
