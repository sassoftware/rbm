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

all: default-all

install: $(generated_files)
	install -D -m0644 postgres.cron	${DESTDIR}/etc/cron.d/postgres
	install -D -m0644 postgresql.chkconfig ${DESTDIR}/etc/chkconfig.d/postgresql
	install -D -m0644 postgresql.conf ${DESTDIR}/etc/postgresql.conf.updateservice
	install -D -m0644 postgresql-updateservice.chkconfig ${DESTDIR}/etc/chkconfig.d/postgresql-updateservice
	install -D -m0644 postgresql-updateservice.sysconfig ${DESTDIR}/etc/sysconfig/pgsql/postgresql-updateservice
	# The recipe installs a symlink at /etc/init.d/postgresql-updateservice pointing
	# at postgresql since dangling symlinks cannot be installed any other way

clean: default-clean

include ../Make.rules
# vim: set sts=8 sw=8 noexpandtab :
