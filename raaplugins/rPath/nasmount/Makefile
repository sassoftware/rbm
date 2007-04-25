#
# Copyright (c) 2007 rPath, Inc.
#
# All rights reserved
#

all: default-all default-subdirs

SUBDIRS = srv \
	web \
	templates

python_files = __init__.py

kid_files =

extra_files = Makefile

dist_files = $(python_files) $(extra_files) $(kid_files)

generated_files = *.pyo *.pyc

.PHONY: clean dist install subdirs

subdirs: default-subdirs

install: all install-subdirs pyfiles-install
	$(PYTHON) -c "import compileall; compileall.compile_dir('$(DESTDIR)$(pluginsdir)', ddir='$(pluginsdir)', quiet=1)"
	$(PYTHON) -OO -c "import compileall; compileall.compile_dir('$(DESTDIR)$(pluginsdir)', ddir='$(pluginsdir)', quiet=1)"

dist: default-dist

clean: clean-subdirs default-clean

include ../Make.rules
