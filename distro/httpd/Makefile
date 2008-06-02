#
# Copyright (c) 2008 rPath, Inc.
#
# All Rights Reserved
#

all: default-all

install: default-install
	install -D -m0644 httpd.chkconfig $(DESTDIR)/etc/chkconfig.d/httpd
	install -D -m0644 conary.conf $(DESTDIR)/etc/httpd/conf.d/conary.conf
	install -D -m0644 updateservice.conf $(DESTDIR)/etc/httpd/conf.d/updateservice.conf

clean: default-clean


include $(TOP)/Make.rules
# vim: set sts=8 sw=8 noexpandtab :
