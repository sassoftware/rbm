#
# Copyright (c) 2007 rPath, Inc.
#
# All Rights Reserved
#

override DEST = $(PYDIR)

static_files = \
	rbm_rc.py \
	upsrv_tool.py \

all: default-all

install: default-install
	install -D -m0755 upsrv_schema.py $(DESTDIR)/usr/bin/upsrv_schema.py

clean: default-clean


include $(TOP)/Make.rules
# vim: set sts=8 sw=8 noexpandtab :
