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

scripts =				\
	backup.py  update-service.backup  updateservice.init  upsrv_schema.py

wrapper_script = path_wrapper.sh

generated_files = $(wrapper_script)

extra_dist = path_wrapper.sh.in

all: default-all $(generated_files)

wrapper-install: path_wrapper.sh
	install -m 0755 -D path_wrapper.sh ${DESTDIR}${LIBEXECDIR}/updateservice/path_wrapper.sh

install: wrapper-install
	#Install the backup scripts
	install -m 0755 -D backup.py	${DESTDIR}/srv/conary/bin/backup.py
	install -m 0755 -D update-service.backup ${DESTDIR}/etc/raa/backup.d/update-service
	#Schema creation
	install -m 0755 -D updateservice.init ${DESTDIR}/etc/init.d/updateservice
	install -m 0755 -D upsrv_schema.py ${DESTDIR}${BINDIR}/upsrv_schema.py

clean: default-clean

path_wrapper.sh: path_wrapper.sh.in
	sed -e's,@SITEPKG@,$(PYDIR),g' -e's,@LIBEXECDIR@,$(LIBEXECDIR),g' path_wrapper.sh.in > path_wrapper.sh

include ../Make.rules
# vim: set sts=8 sw=8 noexpandtab :
