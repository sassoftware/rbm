#
# Copyright (c) 2005-2008 rPath, Inc.
#
# All Rights Reserved
#

all: default-all

install: default-install
	install -D -m0755 init-repos $(DESTDIR)/srv/conary/bin/init-repos
	install -D -m0755 migrate-config $(DESTDIR)/srv/conary/bin/migrate-config
	install -D -m0755 migrate-repos $(DESTDIR)/srv/conary/bin/migrate-repos

clean: default-clean


include $(TOP)/Make.rules
# vim: set sts=8 sw=8 noexpandtab :
