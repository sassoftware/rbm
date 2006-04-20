#!/bin/bash
# chkconfig: 345 22 16
# description: manages the conary repository schema, either by stocking the \
# initial contents or simply upgrading the schema to match the current conary \
# version installed on the system

lock_name="/srv/conary/init_schema_runonce.lock"
schema_python="/usr/lib/python2.4/site-packages/rcra_schema.py"

case "$1" in
start)
  if [ "`ps -A | grep httpd`" != "" ]
  then
    echo "httpd is running. Please stop that service before running this script" > /dev/stderr
    exit 1
  fi
  if [ ! -f $lock_name ]
  then
    $schema_python init
    echo "do not remove this file." > $lock_name
  else
    $schema_python update
  fi
  ;;
stop)
  ;;
*)
  echo "Usage $0 {start | stop}"
  ;;
esac
