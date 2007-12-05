#
# Copyright (c) 2007 rPath, Inc.
#
# All Rights Reserved
#

export PREFIX = /usr
export LIBDIR = $(PREFIX)/lib

export PYDIR = $(LIBDIR)/python$(PYVERSION)/site-packages

all: default-all

install:
	install -D -m0644 rbm_rc.py $(DESTDIR)$(PYDIR)/rbm_rc.py

clean: default-clean

include ../Make.rules
# vim: set sts=8 sw=8 noexpandtab :
