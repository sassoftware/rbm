#
# Copyright (c) 2005-2007 rPath, Inc.
#
# All Rights Reserved
#

export PREFIX = /usr
export BINDIR = $(PREFIX)/bin
export LIBDIR = $(PREFIX)/lib
export LIBEXECDIR = $(PREFIX)/libexec

export PYDIR = $(LIBDIR)/python$(PYVERSION)/site-packages

static_files = \
	conary.conf  httpd  ntpd  repository.cnr  updateservice.conf

all: default-all

install:
	install -D -m0644 repository.cnr ${DESTDIR}/srv/conary/repository.cnr
	install -D -m0644 conary.conf ${DESTDIR}/etc/httpd/conf.d/conary.conf
	install -D -m0644 updateservice.conf ${DESTDIR}/etc/httpd/conf.d/updateservice.conf
	install -D -m0755 httpd ${DESTDIR}/etc/chkconfig.d/httpd
	install -D -m0755 ntpd ${DESTDIR}/etc/chkconfig.d/ntpd

clean: default-clean

include ../Make.rules
# vim: set sts=8 sw=8 noexpandtab :
