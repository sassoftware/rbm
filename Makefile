#
# Copyright (c) 2005-2008 rPath, Inc.
#
# All rights reserved
#

SUBDIRS = distro src raaplugins


TOP = $(shell pwd)
PYTHON = $(shell [ -x /usr/bin/python2.4 ] && echo /usr/bin/python2.4 || echo /usr/lib/conary/python/bin/python2.4)
PYVERSION = $(shell $(PYTHON) -c 'import os, sys; print sys.version[:3]')
PYDIR = /usr/lib/python$(PYVERSION)/site-packages
export PYTHON PYVERSION PYDIR TOP


all: default-all

install: default-install

clean: default-clean


include Make.rules
