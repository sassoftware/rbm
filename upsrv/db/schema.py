#
# Copyright (c) SAS Institute Inc.
#

import logging
import sqlalchemy
import transaction
from conary.dbstore import sqlerrors
from conary.dbstore import sqllib
from sqlalchemy.exc import ProgrammingError, OperationalError
from sqlalchemy.orm.exc import NoResultFound

from .. import config
from . import migrate
from . import models

log = logging.getLogger(__name__)


def getVersion(db, allow_missing=False):
    if allow_missing:
        sp = transaction.savepoint()
    try:
        ver = db.query(models.DatabaseVersion).one()
    except (ProgrammingError, OperationalError), e:
        # Table does not exist
        if allow_missing:
            sp.rollback()
            ver = None
        else:
            raise
    if ver:
        return sqllib.DBversion(ver.version, ver.minor)
    else:
        return sqllib.DBversion(0, 0)


def setVersion(db, version):
    try:
        ver = db.query(models.DatabaseVersion).one()
    except NoResultFound:
        ver = models.DatabaseVersion()
        db.add(ver)
    ver.version = version.major
    ver.minor = version.minor
    return version


def checkVersion(db):
    version = getVersion(db)
    if version != migrate.Version:
        raise sqlerrors.SchemaVersionError('Schema version mismatch', version)
    return version


def updateSchema(db):
    # Monkey-patch db to make it look like what Conary's dbstore expects
    db.setVersion = lambda version, skipCommit=False: setVersion(db, version)
    db.getVersion = lambda raiseOnError=False: getVersion(db,
            allow_missing=not raiseOnError)
    db.cursor = lambda: db
    version = getVersion(db, allow_missing=True)
    if version == migrate.Version:
        return version
    elif version == 0:
        log.info("Creating new database schema with version %s",
                migrate.Version)
        migrate.createSchema(db)
        return setVersion(db, migrate.Version)
    elif version > migrate.Version:
        raise sqlerrors.SchemaVersionError("""
        The database schema version is newer and incompatible with
        this code base. You need to update to a version
        that understands schema %s""" % version, version)
    else:
        return migrate.migrateSchema(db)


if __name__ == '__main__':
    cfg = config.UpsrvConfig.load()
    engine = sqlalchemy.create_engine(cfg.downloadDB)
    db = models.initialize_sql(engine)()
    with transaction.manager:
        updateSchema(db)
