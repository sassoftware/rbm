#
# Copyright (c) 2010 rPath, Inc.
#
# All rights reserved.
#

legacy_files = $(wildcard *.png)


all: default-all

install: default-install
	mkdir -p $(DESTDIR)/usr/share/anaconda/pixmaps
	install -m0644 $(legacy_files) $(DESTDIR)/usr/share/anaconda/pixmaps/

clean: default-clean


include $(TOP)/Make.rules
# vim: set sts=8 sw=8 noexpandtab :
