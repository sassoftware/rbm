#!/bin/sh
#
# Assumes conary is checked out in ../conary
# Assumes raa is checked out in ../raa
# Assumes raa is checked out in ../raa-test

rm -f .coverage

PYTHONPATH=$(pwd)/../:$(pwd)/../../conary:$(pwd)/../../raa:$(pwd)/../../raa-test:$PYTHONPATH nosetests -v -p rPath $@ 2>&1