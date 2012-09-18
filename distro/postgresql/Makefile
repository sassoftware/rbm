#
# Copyright (c) rPath, Inc.
#

all: default-all

install: default-install
	# Postgres configuration
	install -D -m0644 postgres.cron	$(DESTDIR)/etc/cron.d/postgres
	install -D -m0644 postgresql.conf $(DESTDIR)/etc/postgresql.conf.updateservice
	# Turn on postgresql-updateservice
	mkdir -p $(DESTDIR)/etc/init.d
	ln -sf /opt/postgresql-9.2/etc/init.d/postgresql $(DESTDIR)/etc/rc.d/init.d/postgresql-updateservice
	install -D -m0644 postgresql-updateservice.sysconfig $(DESTDIR)/etc/sysconfig/pgsql/postgresql-updateservice
	# Configure for EC2 if necessary
ifdef EC2
	echo 'PGDATA="/mnt/scratch/pgsql-updateservice"' >>$(DESTDIR)/etc/sysconfig/pgsql/postgresql-updateservice
endif

clean: default-clean


include $(TOP)/Make.rules
# vim: set sts=8 sw=8 noexpandtab :
