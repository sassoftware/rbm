#
# Copyright (c) 2005-2007 rPath, Inc.
#
# All Rights Reserved
#

export PREFIX = /usr
export BINDIR = $(PREFIX)/bin
export LIBDIR = $(PREFIX)/lib
export LIBEXECDIR = $(PREFIX)/libexec

export PYDIR = $(LIBDIR)/python$(PYVERSION)/site-packages
export taghandlerdir = ${LIBEXECDIR}/conary/tags
export tagdescriptiondir = /srv/conary/tags


static_files = \
	upsrv.tagdescription	migrate-conaryrc  migrate-config upsrv.taghandler

all: default-all

install: $(static_files)
	install -D -m0744 migrate-conaryrc ${DESTDIR}/srv/conary/bin/migrate-conaryrc
	install -D -m0744 migrate-config ${DESTDIR}/srv/conary/bin/migrate-config
	#Let the recipe install the taghandlers

clean: default-clean

include ../Make.rules
# vim: set sts=8 sw=8 noexpandtab :
