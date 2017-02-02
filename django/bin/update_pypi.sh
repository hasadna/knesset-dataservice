#!/usr/bin/env bash

# update the version on pypi
# assumes pypi authentication is setup with relevant permissions

# use twine for more secure authentication with pypi
if ! which twine; then
    pip install twine
fi

./setup.py sdist bdist_wheel
twine upload dist/*
