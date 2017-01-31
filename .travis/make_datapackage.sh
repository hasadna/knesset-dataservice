#!/usr/bin/env bash

[ -f .travis/.env ] && source .travis/.env

set -e

mkdir -p data

if [ "${DATAPACKAGE_SSH_PROXY_KEY}" != "" ] && [ "${DATAPACKAGE_SSH_PROXY_HOST}" != "" ]; then
    echo "creating ssh socks tunnel"
    echo -e "${DATAPACKAGE_SSH_PROXY_KEY}" > sshproxy.key
    chmod 400 sshproxy.key
    ssh -o StrictHostKeyChecking=no -D 8123 -C -f -N -i sshproxy.key "${DATAPACKAGE_SSH_PROXY_HOST}"
    pushd python > /dev/null
        echo "making datapackage"
        bin/make_datapackage.py --days 3 --debug --zip --http-proxy "socks5://localhost:8123"
    popd > /dev/null
else
    echo "skipping datapackage creation because missing ssh proxy variables"
fi

if [ "${SLACK_API_TOKEN}" != "" ] && [ "${SLACK_LOG_WEBHOOK}" != "" ]; then
    echo "sending notification to slack"
    curl -X POST -g "${SLACK_LOG_WEBHOOK}" --data-urlencode 'payload={"channel": "#oknesset-travis", "username": "travis", "text": ":sunglasses: Travis build: https://travis-ci.org/${TRAVIS_REPO_SLUG}/builds/${TRAVIS_BUILD_ID}"}'
else
    echo "skipping slack integration because missing relevant slack tokens"
fi
