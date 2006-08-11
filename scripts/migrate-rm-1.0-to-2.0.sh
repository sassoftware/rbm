#!/bin/sh
#
# Migration script used to migrate an rM Appliance from version 1.0
# to version 2.0.0

# Full install label to builds repository
INSTALL_LABEL_PATH="products.rpath.com@rpath:rm-devel"

RM_ROOT="/srv/conary"
BACKUPDIR="/tmp/rM-2.0-migration.$$"

# sane path for this script
PATH="/bin:/usr/bin:/sbin:/usr/sbin"

# sanity checks ###############################################################

# Gotta be root
if [ `whoami` != 'root' ]; then
    echo "Migration script must be run as root."
    exit 1
fi

# If rM isn't installed, we can't do very much.
if [ ! -d ${RM_ROOT} ]; then
    echo "rM is not installed; nothing to migrate."
    exit 1
fi

# Check to see if the installed group-rbm-dist is indeed == 1.6.3
curr_ver=`conary q group-rbm-dist | cut -d'=' -f2 | cut -d'-' -f1`
case $curr_ver in
    1.0)
        echo "Found version 1.0 of group-rbm-dist. Migration proceeding."
        ;;
    2.0.0)
        echo "Migration has already taken place. Exiting."
        exit 1
        ;;
    *)
        echo "Migration script will only migrate version 1.0 to version 2.0.0."
        echo "Currently installed version: \"${curr_ver}\"."
        exit 1
        ;;
esac

# start the migration here ####################################################

# update conary (the old school way)
echo "Updating Conary to 1.0.27"
conary update {conary,conary-repository,conary-build}=1.0.27 conary-policy --resolve
if [ $? -ne 0 ]; then
    echo "WARNING: Conary not updated, you'll have to do this again manually."
    echo "Current version of conary is $(conary --version)"
    exit 1
fi

# update using conary 
# use conary migrate to break branch affinity and start fresh
echo "Migrating to group-rbm-dist=$INSTALL_LABEL_PATH"
yes | conary migrate group-rbm-dist=$INSTALL_LABEL_PATH --interactive --resolve
if [ $? -ne 0 ]; then
    echo "Problems occurred when updating rM via Conary; exiting"
    exit 1
fi

# Update the schema
service httpd stop
service rcra_schema.sh start
service httpd start

echo "rM 2.0.0 Migration complete."
exit 0
