#!/usr/bin/env bash

set -e

[ -f .travis/.env ] && source .travis/.env

pip install --upgrade pip
pip install -r python/requirements.txt
pip install python/

if [ "${DATAPACKAGE_SSH_PROXY_KEY}" != "" ] && [ "${DATAPACKAGE_SSH_PROXY_HOST}" != "" ]; then
    echo "creating ssh socks tunnel"
    echo -e "${DATAPACKAGE_SSH_PROXY_KEY}" > sshproxy.key
    chmod 400 sshproxy.key
    ssh -o StrictHostKeyChecking=no -D 8123 -C -f -N -i sshproxy.key "${DATAPACKAGE_SSH_PROXY_HOST}"
fi
