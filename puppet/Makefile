#
# Copyright (c) SAS Institute Inc.
#

all: default-all $(generated_files)

install: default-install $(generated_files)
	mkdir -p $(DESTDIR)/usr/share/puppet/modules
	cp -r appengine_mirror $(DESTDIR)/usr/share/puppet/modules/
	install -D -m0644 appengine_mirror.pp $(DESTDIR)/etc/appengine_mirror.pp

clean: default-clean


include ../Make.rules
# vim: set sts=8 sw=8 noexpandtab :
