#
# Copyright (c) 2008 rPath, Inc.
#
# All Rights Reserved
#

SUBDIRS = rPath
prefix = /usr
export lib = $(shell uname -m | sed -r '/x86_64|ppc64|s390x|sparc64/{s/.*/lib64/;q};s/.*/lib/')
libdir = $(prefix)/$(lib)

override DEST = $(libdir)/raa


all: default-all

install: default-install

clean: default-clean


include $(TOP)/Make.rules
# vim: set sts=8 sw=8 noexpandtab :
