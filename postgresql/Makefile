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

static_files = postgres.chkconfig postgres.cron

all: default-all

install: $(static_files) $(generated_files)
	install -D -m0644 postgres.cron	${DESTDIR}/etc/cron.d/postgres
	install -D -m0644 postgres.chkconfig ${DESTDIR}/etc/chkconfig.d/postgresql

clean: default-clean

include ../Make.rules
# vim: set sts=8 sw=8 noexpandtab :
