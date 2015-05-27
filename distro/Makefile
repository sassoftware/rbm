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


SUBDIRS = conary-web ec2 postgresql rmake3 nginx

scripts = \
	post-install \
	post-update \
	preconfigure

scripts_dir = /usr/share/upsrv/scripts


all: default-all

install: default-install
	mkdir -p $(DESTDIR)$(scripts_dir)
	install    -m0755 $(scripts) $(DESTDIR)$(scripts_dir)/
	install -D -m0755 cleanup.sh $(DESTDIR)/etc/cron.daily/mirror
	install -D -m0755 updateservice.init $(DESTDIR)$(initdir)/updateservice
	install -D -m0755 mirror-admin $(DESTDIR)/usr/sbin/mirror-admin
	install -D -m0644 repository.cnr $(DESTDIR)/srv/conary/repository.cnr
	install -D -m0644 conary.logrotate $(DESTDIR)/etc/logrotate.d/conary-repository
	install -D -m0644 firewall $(DESTDIR)/etc/sysconfig/iptables
	install -D -m0644 firewall6 $(DESTDIR)/etc/sysconfig/ip6tables
	install -D -m0644 gunicorn.conf $(DESTDIR)/etc/gunicorn.conf
	install -D -m0644 gunicorn.sysconfig $(DESTDIR)/etc/sysconfig/gunicorn
	install -D -m0644 repositorydb.cnr $(DESTDIR)/srv/conary/config/50_repositorydb.cnr

clean: default-clean


include $(TOP)/Make.rules
# vim: set sts=8 sw=8 noexpandtab :
