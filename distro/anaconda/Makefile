#
# Copyright (c) 2010 rPath, Inc.
#
# All rights reserved.
#

all: default-all

install: default-install
	install -D -m0644 rcra.py $(DESTDIR)/usr/share/anaconda/installclasses/rcra.py
	install -D -m0644 grub.defaults $(DESTDIR)/usr/share/anaconda/grub.defaults
	install -D -m0644 grub.template $(DESTDIR)/usr/share/anaconda/grub.template
	cp -r pixmaps $(DESTDIR)/usr/share/anaconda/pixmaps

clean: default-clean


include $(TOP)/Make.rules
# vim: set sts=8 sw=8 noexpandtab :
