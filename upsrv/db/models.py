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


import base64
import datetime
from conary import trovetup
from conary import versions
from conary.deps import deps
from pyramid.decorator import reify
from sqlalchemy import Column, Boolean, BigInteger, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from zope.sqlalchemy import ZopeTransactionExtension


Base = declarative_base()


class DatabaseVersion(Base):
    __tablename__ = 'databaseversion'
    version         = Column(Integer,   primary_key=True)
    minor           = Column(Integer,   primary_key=True)


class DownloadFile(Base):
    __tablename__ = 'download_files'
    file_sha1       = Column(Text,      primary_key=True)
    file_modified   = Column(DateTime,  nullable=False)
    file_basename   = Column(Text,      nullable=False)
    file_size       = Column(BigInteger, nullable=False)
    trove_name      = Column(Text,      nullable=False)
    trove_version   = Column(Text,      nullable=False)
    trove_timestamp = Column(Text,      nullable=False)
    trove_flavor    = Column(Text,      nullable=False)

    meta_items      = relationship('DownloadMetadata', backref='file',
            cascade='all')

    @reify
    def trove_tup(self):
        return trovetup.TroveTuple(
                self.trove_name.encode('ascii'),
                versions.VersionFromString(self.trove_version.encode('ascii'),
                    timeStamps=[float(self.trove_timestamp)]),
                deps.parseFlavor(self.trove_flavor.encode('ascii')),
                )


class DownloadMetadata(Base):
    __tablename__ = 'download_metadata'
    file_sha1       = Column(Text, ForeignKey('download_files.file_sha1'), primary_key=True)
    meta_key        = Column(Text,      primary_key=True)
    meta_value      = Column(Text,      nullable=False)
    meta_type       = Column(Text,      nullable=False)

    def _value_get(self):
        if self.meta_type == 'int':
            return int(self.meta_value)
        elif self.meta_type == 'float':
            return base64.b64decode(self.meta_value)
        else:
            # str
            return self.meta_value
    def _value_set(self, value):
        assert value is not None
        if isinstance(value, (int, long)):
            self.meta_type = 'int'
        elif isinstance(value, float):
            self.meta_type = 'float'
        else:
            self.meta_type = 'str'
        self.meta_value = unicode(value)
    value = property(_value_get, _value_set)


class CustomerEntitlement(Base):
    __tablename__ = 'customer_entitlements'
    cust_id         = Column(Text,      primary_key=True)
    entitlement     = Column(Text,      primary_key=True)

class Record(Base):
    __tablename__ = 'records'
    uuid = Column(Text, primary_key=True,
            info=dict(recordCreate=dict(required=True)))

    producers = Column(Text, nullable=False,
            info=dict(recordCreate=dict(required=True),
                recordEncoding='json'))
    system_id = Column(Text, nullable=False,
            info=dict(recordCreate=dict(required=True)))
    client_address = Column(Text, nullable=False,
            info=dict(recordCreate=dict(readOnly=True)))
    version = Column(Text, nullable=False,
            info=dict(recordCreate=dict(required=True)))
    entitlements_json = Column(Text,
            info=dict(recordCreate=dict(readOnly=True)))
    entitlement_valid = Column(Boolean,
            info=dict(recordCreate=dict(readOnly=True)))
    # This is set by the record's created_time
    created_time = Column(DateTime, nullable=False,
            default=datetime.datetime.utcnow)
    # This is NOT updated from the record, it is set as readOnly
    updated_time = Column(DateTime, nullable=False,
            default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow,
            info=dict(recordCreate=dict(readOnly=True)))

# Not really needed since we're not generating the schema
Index('records_systemid_idx', Record.system_id)
Index('idx_records_updated_time', Record.created_time)

def initialize_sql(engine, use_tm=True):
    Base.metadata.bind = engine
    extension = ZopeTransactionExtension() if use_tm else None
    maker = sessionmaker(bind=engine, extension=extension)
    return maker
