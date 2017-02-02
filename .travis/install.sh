#!/usr/bin/env bash

set -e  # exit on errors

[ -f .travis/.env ] && source .travis/.env

pip install --upgrade pip
pip install -r django/requirements.txt
pip install -r python/requirements.txt
pip install python/
pip install django/
pip install https://github.com/hasadna/Open-Knesset/archive/e28339da7ca92df96fc79b89351286e2715fcff0.zip#egg=Open-Knesset

if [ "${DATAPACKAGE_SSH_PROXY_KEY}" != "" ] && [ "${DATAPACKAGE_SSH_PROXY_HOST}" != "" ]; then
    echo "creating ssh socks tunnel"
    echo -e "${DATAPACKAGE_SSH_PROXY_KEY}" > sshproxy.key
    chmod 400 sshproxy.key
    ssh -o StrictHostKeyChecking=no -D 8123 -C -f -N -i sshproxy.key "${DATAPACKAGE_SSH_PROXY_HOST}"
fi
