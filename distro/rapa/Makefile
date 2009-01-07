#
# Copyright (c) 2008 rPath, Inc.
#
# All Rights Reserved
#

all: default-all

install: default-install
	install -D -m0755 backup-script $(DESTDIR)/etc/raa/backup.d/update-service
	install -D -m0644 collect.flat $(DESTDIR)/etc/raa/collect.d/rUSFiles

clean: default-clean


include $(TOP)/Make.rules
# vim: set sts=8 sw=8 noexpandtab :
