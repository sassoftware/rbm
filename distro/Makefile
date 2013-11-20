#
# Copyright (c) SAS Institute Inc.
#

SUBDIRS = conary-web ec2 postgresql rmake3 nginx

scripts = \
	post-install \
	post-update \
	preconfigure \
	generate-certs

scripts_dir = /usr/share/upsrv/scripts


all: default-all

install: default-install
	mkdir -p $(DESTDIR)$(scripts_dir)
	install    -m0755 $(scripts) $(DESTDIR)$(scripts_dir)/
	install -D -m0755 cleanup.sh $(DESTDIR)/etc/cron.daily/mirror
	install -D -m0755 updateservice.init $(DESTDIR)$(initdir)/updateservice
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
