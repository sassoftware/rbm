#
# Copyright (c) 2005-2006 rPath, Inc.
#
# All rights reserved
#

all: subdirs

SUBDIRS=config postgresql rcgenerator scripts taghandler

extra_files = \
	Make.rules 		\
	Makefile		\

dist_files = $(extra_files)

.PHONY: clean dist install subdirs $(SUBDIRS)

subdirs: default-subdirs

install: install-subdirs

dist:
	rm -rf $(DISTDIR)
	mkdir $(DISTDIR)
	for d in $(SUBDIRS); do make -C $$d DIR=$$d dist || exit 1; done
	for f in $(dist_files); do \
		mkdir -p $(DISTDIR)/`dirname $$f`; \
		cp -a $$f $(DISTDIR)/$$f; \
	done; \
	tar cjf $(DISTDIR).tar.bz2 `basename $(DISTDIR)`
	rm -rf $(DISTDIR)

$(SUBDIRS):
	rm -rf $(DISTDIR)
	mkdir $(DISTDIR)
	make -C $@ DIR=$@ dist || exit 1
	for f in $(dist_files); do \
		mkdir -p $(DISTDIR)/`dirname $$f`; \
		cp -a $$f $(DISTDIR)/$$f; \
	done; \
	sed -i "s/SUBDIRS\s*=.*/SUBDIRS=$@/" $(DISTDIR)/Makefile
	sed -i "/\s*sed -i.*/d" $(DISTDIR)/Makefile
	tar cjf $@.tar.bz2 `basename $(DISTDIR)`
	rm -rf $(DISTDIR)

clean: clean-subdirs default-clean
	rm -f _sqlite.so _sqlite3.so
	rm -rf sqlite sqlite3

include Make.rules
