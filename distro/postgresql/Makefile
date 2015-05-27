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


all: default-all

install: default-install
	install -D -m0644 postgres.cron	$(DESTDIR)/etc/cron.d/postgres
	install -D -m0644 postgresql.conf $(DESTDIR)/etc/postgresql.conf.updateservice
	install -D -m0644 pgbouncer.conf ${DESTDIR}/etc/pgbouncer/pgbouncer.ini
	mkdir -p $(DESTDIR)$(initdir)
	ln -sf /opt/postgresql-9.2/etc/init.d/postgresql $(DESTDIR)$(initdir)/postgresql-updateservice
	install -D -m0644 postgresql-updateservice.sysconfig $(DESTDIR)/etc/sysconfig/pgsql/postgresql-updateservice
ifdef EC2
	echo 'PGDATA="/mnt/scratch/pgsql-updateservice"' >>$(DESTDIR)/etc/sysconfig/pgsql/postgresql-updateservice
endif

clean: default-clean


include $(TOP)/Make.rules
# vim: set sts=8 sw=8 noexpandtab :
