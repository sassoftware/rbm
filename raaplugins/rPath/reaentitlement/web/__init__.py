#
# Copyright (c) 2008 rPath, Inc.
#
# All rights reserved
#

from raa.db.data import RDT_STRING

def migrateSpecialUseTableToProperties(plugin, db, oldTableName, oldColumns, newKeys):
    ''' Migrates special use tables that store key value pairs to the pluginProperties table.

        @type plugin: C{rAAWebPlugin}
        @param plugin: The plugin to set the properties for
        @type db: dbstore Database object
        @param db: The db to operate on
        @type oldTableName: string
        @param oldTableName: The name of the table to be migrated, this table will be dropped at the end of the migration process
        @type oldColumns: list of strings
        @param oldColumns: A list of the columns (settings) that need to be migrated
        @type newKeys: list of strings
        @param newKeys: A list of the property names to use when storing the C{oldColumns}.  The number of items in this list must match the number of items in C{oldColumns}
    '''
    #Check to see if the old table is there.  If so, remove it
    if oldTableName in db.tables:
        cu = db.cursor()
        assert len(oldColumns) == len(newKeys), "Mismatched number of columns to keys"
        for i, col in enumerate(oldColumns):
            #Grab the existing setting, and store it as a property
            cu.execute("SELECT %s FROM %s" % (col, oldTableName))
            key = cu.fetchone()[0]
            if key:
                plugin.setPropertyValue(newKeys[i], key, RDT_STRING, commit=False)
        cu.execute('DROP TABLE %s' % oldTableName)
        db.commit()


