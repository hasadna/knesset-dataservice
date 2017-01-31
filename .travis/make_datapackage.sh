#!/usr/bin/env bash

mkdir data

pushd python > /dev/null
    if [ "${DATAPACKAGE_SSH_PROXY_KEY}" != "" && "${DATAPACKAGE_SSH_PROXY_HOST}" != "" ]; then
        echo -e "${DATAPACKAGE_SSH_PROXY_KEY}" > sshproxy.key
        chmod 400 sshproxy.key
        ssh -o StrictHostKeyChecking=no -D 8123 -C -f -N -i sshproxy.key "${DATAPACKAGE_SSH_PROXY_HOST}"
        bin/make_datapackage.py --days 3 --debug --zip --http-proxy "socks5://localhost:8123"
    fi
popd > /dev/null
