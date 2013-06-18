# Copyright (c) SAS Institute Inc.
#

from conary.dbstore import sqllib

Version = sqllib.DBversion(1, 0)


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
        file_type               text            NOT NULL,
        file_modified           timestamptz     NOT NULL,
        file_basename           text            NOT NULL,
        file_size               bigint          NOT NULL,
        trove_name              text            NOT NULL,
        trove_version           text            NOT NULL,
        trove_timestamp         text            NOT NULL,
        trove_flavor            text            NOT NULL
    )""")

    return Version
