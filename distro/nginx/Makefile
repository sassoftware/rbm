#
# Copyright (c) SAS Institute Inc.
#


all: default-all

install: default-install
	mkdir -p $(DESTDIR)/srv/rbuilder/tmp
	mkdir -p $(DESTDIR)/var/log/rbuilder
	install -D -m0644 nginx.conf $(DESTDIR)/etc/nginx/nginx.conf
	install -D -m0644 nginx-rus.conf $(DESTDIR)/etc/nginx/conf.d/01_rus.conf
	install -D -m0644 nginx.mime.types $(DESTDIR)/etc/nginx/mime.types
	install -D -m0644 nginx.sysconfig $(DESTDIR)/etc/sysconfig/nginx

clean: default-clean


include $(TOP)/Make.rules
# vim: set sts=8 sw=8 noexpandtab :
