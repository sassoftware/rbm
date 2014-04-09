# Copyright (c) SAS Institute Inc.
#

import sys
import logging
log = logging.getLogger(__name__)

from conary.dbstore import migration, sqllib, sqlerrors

Version = sqllib.DBversion(2, 0)

class SchemaMigration(migration.SchemaMigration):
    db = None
    msg = None
    Version = (None, None)

    def message(self, msg = None):
        if msg is None:
            msg = self.msg
        if msg == "":
            msg = "Finished migration to schema version %s" % (self.Version,)
        log.info(msg)
        self.msg = msg

def createSchema(db):
    db.execute("""
    CREATE TABLE databaseversion (
        version                 integer         NOT NULL,
        minor                   integer         NOT NULL,
        PRIMARY KEY ( version, minor )
    )""")

    db.execute("""
    CREATE TABLE download_files (
        file_sha1               text            PRIMARY KEY,
        file_modified           timestamptz     NOT NULL,
        file_basename           text            NOT NULL,
        file_size               bigint          NOT NULL,
        trove_name              text            NOT NULL,
        trove_version           text            NOT NULL,
        trove_timestamp         text            NOT NULL,
        trove_flavor            text            NOT NULL
    )""")

    db.execute("""
    CREATE TABLE download_metadata (
        file_sha1               text            NOT NULL
            REFERENCES download_files ON UPDATE CASCADE ON DELETE CASCADE,
        meta_key                text            NOT NULL,
        meta_value              text            NOT NULL,
        meta_type               text            NOT NULL,
        PRIMARY KEY ( file_sha1, meta_key )
    )""")

    db.execute("""
    CREATE TABLE customer_entitlements (
        cust_id                 text            NOT NULL,
        entitlement             text            NOT NULL,
        PRIMARY KEY ( cust_id, entitlement )
    )""")

    db.execute("""
    CREATE TABLE records (
            uuid TEXT NOT NULL,
            producers TEXT NOT NULL,
            system_id TEXT NOT NULL,
            client_address TEXT NOT NULL,
            version TEXT NOT NULL,
            created_time TIMESTAMP WITH TIME ZONE NOT NULL,
            updated_time TIMESTAMP WITH TIME ZONE NOT NULL,
            PRIMARY KEY (uuid)
    )""")

    db.execute("""
    CREATE INDEX records_systemid_idx ON records (system_id)
    """)
    db.setVersion(Version)
    return Version

class MigrateTo_0(SchemaMigration):
    Version = (0, 1)
    def migrate(self):
        return True

class MigrateTo_1(SchemaMigration):
    Version = (1, 0)
    def migrate(self):
        db = self.db
        db.execute("""
        CREATE TABLE download_files (
            file_sha1               text            PRIMARY KEY,
            file_modified           timestamptz     NOT NULL,
            file_basename           text            NOT NULL,
            file_size               bigint          NOT NULL,
            trove_name              text            NOT NULL,
            trove_version           text            NOT NULL,
            trove_timestamp         text            NOT NULL,
            trove_flavor            text            NOT NULL
        )""")

        db.execute("""
        CREATE TABLE download_metadata (
            file_sha1               text            NOT NULL
                REFERENCES download_files ON UPDATE CASCADE ON DELETE CASCADE,
            meta_key                text            NOT NULL,
            meta_value              text            NOT NULL,
            meta_type               text            NOT NULL,
            PRIMARY KEY ( file_sha1, meta_key )
        )""")

        db.execute("""
        CREATE TABLE customer_entitlements (
            cust_id                 text            NOT NULL,
            entitlement             text            NOT NULL,
            PRIMARY KEY ( cust_id, entitlement )
        )""")
        return True

class MigrateTo_2(SchemaMigration):
    Version = (2, 0)

    def migrate(self):
        db = self.db
        db.execute("""
        CREATE TABLE records (
                uuid TEXT NOT NULL,
                producers TEXT NOT NULL,
                system_id TEXT NOT NULL,
                client_address TEXT NOT NULL,
                version TEXT NOT NULL,
                created_time TIMESTAMP WITH TIME ZONE NOT NULL,
                updated_time TIMESTAMP WITH TIME ZONE NOT NULL,
                PRIMARY KEY (uuid)
        )""")
        db.execute("""
        CREATE INDEX records_systemid_idx ON records (system_id)
        """)
        return True

def migrateSchema(db):
    version = db.getVersion()
    migrateFunc = _getMigration(version.major)
    if migrateFunc is None:
        raise sqlerrors.SchemaVersionError(
            "Could not find migration code that deals with repository "
            "schema %s" % version, version)
    # migrate all the way to the latest minor for the current major
    tryMigrate(db, migrateFunc(db))
    version = db.getVersion()
    # migrate to the latest major
    while version.major < Version.major:
        migrateFunc = _getMigration(int(version.major)+1)
        newVersion = tryMigrate(db, migrateFunc(db))
        assert(newVersion.major == version.major+1)
        version = newVersion
    return version

def _getMigration(major):
    try:
        ret = sys.modules[__name__].__dict__['MigrateTo_' + str(major)]
    except KeyError:
        return None
    return ret

def majorMinor(major):
    migr = _getMigration(major)
    if migr is None:
        return (major, 0)
    return migr.Version

def tryMigrate(db, func):
    # Do all migration steps in one transaction so a failure in createSchema
    # will abort the whole thing. Otherwise we wouldn't rerun the createSchema
    # because the schema version has already been updated.
    return func(skipCommit=True)
