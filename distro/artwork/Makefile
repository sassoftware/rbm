#
# Copyright (c) 2010 rPath, Inc.
#
# All rights reserved.
#

SUBDIRS = anaconda_legacy

all: default-all

install: default-install
	install -D -m0644 anaconda_first.png $(DESTDIR)/usr/share/anaconda/pixmaps/progress_first.png
	install -D -m0644 anaconda_splash.png $(DESTDIR)/usr/share/anaconda/pixmaps/splash.png
	install -D -m0644 bootloader_splash.png $(DESTDIR)/boot/extlinux/upsrv_background.png
	install -D -m0644 splashy_background.png $(DESTDIR)/usr/share/splashy/themes/upsrv/background.png

clean: default-clean


include $(TOP)/Make.rules
# vim: set sts=8 sw=8 noexpandtab :
