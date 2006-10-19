#!/bin/sh
#
# Migration script used to migrate an rM Appliance from version 1.0
# to version 2.0.0

# Full install label to builds repository
INSTALL_LABEL_PATH="products.rpath.com@rpath:rm-2"
TROVES_FOR_UPDATE="group-rbm-dist=products.rpath.com@rpath:rbm-1 group-rbm-dist=products.rpath.com@rpath:rm-2 conary=products.rpath.com@rpath:conary-1.1 raaplugins=products.rpath.com@rpath:raa-1"

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

for l in $TROVES_FOR_UPDATE; do
    echo -n "Checking access to $l... "
    conary rq $l >& /dev/null
    if [ $? -ne 0 ]; then
        echo "failed"
        echo ""
        echo "It appears that your appliance cannot access this product update."
        echo "Contact a rPath sales engineer for assistance."
        exit 1
    else
        echo "passed"
    fi
done

echo "Access confirmed to product update. Migration proceeding."
echo ""

# Check to see if the installed group-rbm-dist is indeed == 1.0
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
echo -n "Checking Conary..."
cversion=`conary --version`

case $cversion in
    1.0.*)
        cversion_minor=`echo $cversion | cut -d. -f3`
        if [ $cversion_minor -lt 27 ]; then
            update_conary=0
        else
            update_conary=1
        fi
        ;;
    1.1.*)
        update_conary=1
        ;;
    *)
        echo "Unknown conary version; something's wrong. Bailing."
        exit 1
        ;;
esac

echo "found version $cversion"

if [ $update_conary -eq 0 ]; then
    echo "Updating Conary to 1.0.27"
    conary update {conary,conary-repository,conary-build}=1.0.27 conary-policy --resolve
    if [ $? -ne 0 ]; then
        echo "WARNING: Conary not updated, you'll have to do this again manually."
        echo "Current version of conary is $(conary --version)"
        exit 1
    fi
else
    echo "Conary is sufficiently up-to-date for this migration; continuing."
fi

# backup the configuration files, as Conary may not keep them around
echo "Backing up configuration files to $BACKUPDIR"
[ ! -d $BACKUPDIR ] && mkdir $BACKUPDIR
cp ${RM_ROOT}/repository.cnr ${BACKUPDIR}

# update using conary 
# use conary migrate to break branch affinity and start fresh
echo "Migrating to group-rbm-dist=$INSTALL_LABEL_PATH"
yes | conary migrate group-rbm-dist=$INSTALL_LABEL_PATH --interactive --resolve
if [ $? -ne 0 ]; then
    echo "Problems occurred when updating rM via Conary; exiting"
    exit 1
fi

# backup the configuration files, as Conary may not keep them around
echo "Restoring configuratin files to ${RM_ROOT}"
cp ${BACKUPDIR}/repository.cnr ${RM_ROOT}

# Update the schema
service httpd stop
echo -n  "Updating repository schema..."
# Wait for apache to shutdown
while [ "`ps -A | grep httpd`" != "" ]; do
  sleep 0.5
done
service rcra_schema.sh start
echo "done"

# Update repo perms
echo -n "Updating repository user permissions..."
python migrate_users.py
echo "done"

# Update iptables
echo "Updating firewall configuration..."
system-config-securitylevel-tui -q -p 22:tcp -p 80:tcp -p 443:tcp -p 8003:tcp

service httpd start

# start raa
service raa-lighttpd start
service raa start

echo "rM 2.0.0 Migration complete."
exit 0
