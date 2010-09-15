#
# Copyright (c) 2010 rPath, Inc.
#
# All rights reserved.
#

SUBDIRS = anaconda artwork conary-web ec2 httpd postgresql rapa taghandler


all: default-all

install: default-install
	install -D -m0644 repository.cnr $(DESTDIR)/srv/conary/repository.cnr
	install -D -m0644 ntpd.chkconfig $(DESTDIR)/etc/chkconfig.d/ntpd
	install -D -m0755 updateservice.init $(DESTDIR)/etc/init.d/updateservice
	install -D -m0755 cleanup.sh $(DESTDIR)/etc/cron.daily/mirror
	install -D -m0644 entitlements.xml $(DESTDIR)/etc/conary/entitlements.xml
	install -D -m0644 firewall $(DESTDIR)/etc/firewall
	sed \
		-e 's/-p icmp /-p icmpv6 /g' \
		-e 's/icmp-host-prohibited/adm-prohibited/g' \
		firewall > $(DESTDIR)/etc/firewall6
	# branding
	install -D -m0644 splashy.xml $(DESTDIR)/usr/share/splashy/themes/upsrv/theme.xml
	install -D -m0644 FreeSans.ttf $(DESTDIR)/usr/share/splashy/themes/upsrv/FreeSans.ttf
	install -D -m0644 bootman.conf $(DESTDIR)/etc/bootloader.d/05_upsrv.conf

clean: default-clean


include $(TOP)/Make.rules
# vim: set sts=8 sw=8 noexpandtab :
