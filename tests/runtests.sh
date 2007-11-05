#!/bin/sh
#
# Assumes conary is checked out in ../conary
# Assumes raa is checked out in ../raa
# Assumes raa is checked out in ../raa-test

rm -f .coverage

PYTHONPATH=$(pwd)/../raaplugins/:$RAA_PATH:$(pwd)/../../raa-test-2.1:..:$CONARY_TEST_PATH:$CONARY_PATH:$PYTHONPATH nosetests -v -p rPath $@ 2>&1
