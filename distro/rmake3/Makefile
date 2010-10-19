#
# Copyright (c) 2010 rPath, Inc.
#
# All rights reserved.
#

all: default-all

install: default-install
	install -D -m0644 worker.conf $(DESTDIR)/etc/rmake3/node.d/20_rbuilder.conf
	install -D -m0644 rmake3-node.sysconfig $(DESTDIR)/etc/sysconfig/rmake3-node

clean: default-clean


include $(TOP)/Make.rules
# vim: set sts=8 sw=8 noexpandtab :
