#!/usr/bin/env bash

[ -f .travis/.env ] && source .travis/.env

set -e

pushd python > /dev/null
    bin/run_tests.sh
popd > /dev/null
