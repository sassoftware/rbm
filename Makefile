#
# Copyright (c) SAS Institute Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


SUBDIRS = distro puppet


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
