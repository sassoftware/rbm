#
# Copyright (c) SAS Institute Inc.
#


from conary import trovetup
from conary import versions
from conary.deps import deps
from pyramid.decorator import reify
from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension


Base = declarative_base()


class DownloadFile(Base):
    __tablename__ = 'download_files'
    file_id         = Column(Integer,   primary_key=True)
    file_type       = Column(Text,      nullable=False)
    file_modified   = Column(DateTime,  nullable=False)
    file_basename   = Column(Text,      nullable=False)
    trove_name      = Column(Text,      nullable=False)
    trove_version   = Column(Text,      nullable=False)
    trove_flavor    = Column(Text,      nullable=False)

    @reify
    def trove_tup(self):
        return trovetup.TroveTuple(self.trove_name.encode('ascii'),
                versions.ThawVersion(self.trove_version.encode('ascii')),
                deps.ThawFlavor(self.trove_flavor.encode('ascii')))


def initialize_sql(engine, use_tm=True):
    Base.metadata.bind = engine
    extension = ZopeTransactionExtension() if use_tm else None
    maker = sessionmaker(bind=engine, extension=extension)
    return maker
