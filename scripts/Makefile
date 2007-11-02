#
# Copyright (c) 2005-2007 rPath, Inc.
#
# All Rights Reserved
#

export PREFIX = /usr
export BINDIR = $(PREFIX)/bin
export LIBDIR = $(PREFIX)/lib
export LIBEXECDIR = $(PREFIX)/libexec

scripts =				\
	backup.py  update-service.backup  updateservice.init  upsrv_schema.py

all: default-all

install:
	#Install the backup scripts
	install -m 0755 -D backup.py	${DESTDIR}/srv/conary/bin/backup.py
	install -m 0755 -D update-service.backup ${DESTDIR}/etc/raa/backup.d/update-service
	#Schema creation
	install -m 0755 -D updateservice.init ${DESTDIR}/etc/init.d/updateservice
	install -m 0755 -D upsrv_schema.py ${DESTDIR}${BINDIR}/upsrv_schema.py

clean: default-clean

include ../Make.rules
# vim: set sts=8 sw=8 noexpandtab :
