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

static_files = \
	postgresql  usepostgres.py

extra_dist = postgres.cron.in

generated_files = postgres.cron

all: default-all

postgres.cron: postgres.cron.in
	sed -e's,@BINDIR@,$(BINDIR),g' postgres.cron.in > postgres.cron

install: $(static_files) $(generated_files)
	install -D -m0755 postgresql ${DESTDIR}/etc/chkconfig.d/postgresql
	install -D -m0755 usepostgres.py ${DESTDIR}/srv/conary/bin/usepostgres.py
	install -D -m0644 postgres.cron	${DESTDIR}/etc/cron.d/postgres

clean: default-clean

include ../Make.rules
# vim: set sts=8 sw=8 noexpandtab :
