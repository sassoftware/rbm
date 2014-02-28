# Copyright (c) SAS Institute Inc.
#

from conary.dbstore import sqllib

Version = sqllib.DBversion(2, 0)

from .db import models

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
    return Version

def migrateSchema(db):
    # XXX Needs to be better for the next migration; for now we're
    # executing just one
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

    db.query(models.DatabaseVersion).update(
        values=dict(version=Version.major, minor=Version.minor))
    return Version
