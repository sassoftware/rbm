#!/bin/sh

rm .coverage
./runtests-nocoverage.sh -l -p rPath. $@
