#
# Copyright (c) SAS Institute Inc.
#

import base64
from conary import trovetup
from conary import versions
from conary.deps import deps
from pyramid.decorator import reify
from sqlalchemy import Column, BigInteger, Integer, Text, DateTime, ForeignKey
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

    meta_items      = relationship('DownloadMetadata', backref='file')

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


def initialize_sql(engine, use_tm=True):
    Base.metadata.bind = engine
    extension = ZopeTransactionExtension() if use_tm else None
    maker = sessionmaker(bind=engine, extension=extension)
    return maker
