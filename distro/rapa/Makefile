#
# Copyright (c) 2008 rPath, Inc.
#
# All Rights Reserved
#

all: default-all

install: default-install
	install -D -m0755 backup-script $(DESTDIR)/etc/raa/backup.d/update-service
	install -D -m0644 collect.flat $(DESTDIR)/etc/raa/collect.d/rUSFiles
	install -D -m0644 prodlogo.png $(DESTDIR)/usr/share/raa/content/images/prodlogo.png
	install -D -m0644 collectiontool.html $(DESTDIR)/usr/share/raa/content/collectiontool.html
	sed -e 's/@PRODVERSION@/$(VERSION)s/g' custom.cfg >$(DESTDIR)/etc/raa/custom.cfg

clean: default-clean


include $(TOP)/Make.rules
# vim: set sts=8 sw=8 noexpandtab :
