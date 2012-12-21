#
# Copyright (c) 2010 rPath, Inc.
#
# All rights reserved.
#

SUBDIRS = distro src raaplugins


export TOP = $(shell pwd)
export VERSION = not.set

# Callers should change PYTHON to the desired python binary.
export lib = $(shell uname -m | sed -r '/x86_64|ppc64|s390x|sparc64/{s/.*/lib64/;q};s/.*/lib/')
export prefix = /usr
export libdir = $(prefix)/$(lib)
export initdir = /etc/rc.d/init.d
export PYTHON = /usr/bin/python
export PYVER = $(shell $(PYTHON) -c 'import sys; print(sys.version[0:3])')
export PYDIR = $(libdir)/python$(PYVER)/site-packages


all: default-all

install: default-install

clean: default-clean


include Make.rules
