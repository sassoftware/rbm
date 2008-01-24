#!/bin/sh
#Assumes conary is checked out in ../conary-1.1
#Assumes conary-test is checked out in ../conary-test-1.1

CONARY_BRANCH=-2.0
RAA_BRANCH=-2.1

if [ -z "$CONARY_PATH" ]
then
    CONARY_PATH=`pwd`/../conary$CONARY_BRANCH/
fi

if [ -z "$CONARY_TEST_PATH" ]
then
    CONARY_TEST_PATH=`pwd`/../conary-test$CONARY_BRANCH/
fi

if [ -z "$RAA_PATH" ]
then
    RAA_PATH=`pwd`/../raa$RAA_BRANCH
fi

if [ -z "$RAA_TEST_PATH" ]
then
    RAA_TEST_PATH=`pwd`/../raa-test$RAA_BRANCH
fi

export CONARY_PATH RAA_PATH CONARY_TEST_PATH RAA_TEST_PATH
PYTHONPATH=`pwd`/raaplugins:$RAA_PATH:$RAA_TEST_PATH:$CONARY_PATH:$CONARY_TEST_PATH:$PYTHONPATH nosetests -v "$@"

