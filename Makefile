#
# Copyright (c) 2010 rPath, Inc.
#
# All rights reserved.
#

SUBDIRS = distro src raaplugins


export TOP = $(shell pwd)
export VERSION = 5.8.5.2

# Callers should change PYTHON to the desired python binary.
export PYTHON = /usr/bin/python
export PYVER = $(shell $(PYTHON) -c 'import sys; print(sys.version[0:3])')
export PYDIR = $(shell $(PYTHON) \
	-c 'import sys; print [x for x in sys.path if x.endswith("site-packages") ][0]')


all: default-all

install: default-install

clean: default-clean


include Make.rules
