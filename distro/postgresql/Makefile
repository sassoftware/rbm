#
# Copyright (c) rPath, Inc.
#

all: default-all

install: default-install
	install -D -m0644 postgres.cron	$(DESTDIR)/etc/cron.d/postgres
	install -D -m0644 postgresql.conf $(DESTDIR)/etc/postgresql.conf.updateservice
	mkdir -p $(DESTDIR)$(initdir)
	ln -sf /opt/postgresql-9.2/etc/init.d/postgresql $(DESTDIR)$(initdir)/postgresql-updateservice
	install -D -m0644 postgresql-updateservice.sysconfig $(DESTDIR)/etc/sysconfig/pgsql/postgresql-updateservice
ifdef EC2
	echo 'PGDATA="/mnt/scratch/pgsql-updateservice"' >>$(DESTDIR)/etc/sysconfig/pgsql/postgresql-updateservice
endif

clean: default-clean


include $(TOP)/Make.rules
# vim: set sts=8 sw=8 noexpandtab :
