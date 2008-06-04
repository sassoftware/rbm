#
# Copyright (c) 2008 rPath, Inc.
#
# All Rights Reserved
#


all: default-all

install: default-install
ifdef EC2
	install -D -m0755 ec2.init $(DESTDIR)/etc/init.d/updateservice-ec2
	install -D -m0644 05_ec2.cnr $(DESTDIR)/srv/conary/config/05_ec2.cnr
endif

clean: default-clean


include $(TOP)/Make.rules
# vim: set sts=8 sw=8 noexpandtab :
