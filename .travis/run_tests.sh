#!/usr/bin/env bash

set -e

pushd python > /dev/null
    bin/run_tests.sh
popd > /dev/null
