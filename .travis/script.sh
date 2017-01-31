#!/usr/bin/env bash

[ -f .travis/.env ] && source .travis/.env

set -e

echo "running tests"
pushd python > /dev/null
    bin/run_tests.sh
popd > /dev/null

if [[ "${BUILD_DATAPACKAGE_BRANCHES}" == *"${TRAVIS_BRANCH}"* ]]; then
    mkdir -p data

    if [ "${DATAPACKAGE_SSH_PROXY_KEY}" != "" ] && [ "${DATAPACKAGE_SSH_PROXY_HOST}" != "" ]; then
        echo "creating ssh socks tunnel"
        echo -e "${DATAPACKAGE_SSH_PROXY_KEY}" > sshproxy.key
        chmod 400 sshproxy.key
        ssh -o StrictHostKeyChecking=no -D 8123 -C -f -N -i sshproxy.key "${DATAPACKAGE_SSH_PROXY_HOST}"
        pushd python > /dev/null
            echo "making datapackage for last ${DATAPACKAGE_LAST_DAYS} days"
            bin/make_datapackage.py --days "${DATAPACKAGE_LAST_DAYS}" --debug --zip --http-proxy "socks5://localhost:8123"
        popd > /dev/null
    else
        echo "skipping datapackage creation because missing ssh proxy variables"
    fi

    if [ "${KNESSET_DATA_BUCKET}" != "" ]; then
        pip install awscli
        DATAPACKAGE_FILENAME="datapackage_last_${DATAPACKAGE_LAST_DAYS}_days_`date "+%Y-%m-%d_%H-%M"`.zip"
        aws s3 cp "data/datapackage.zip" "s3://${KNESSET_DATA_BUCKET}/${DATAPACKAGE_FILENAME}" --acl=public-read
        DATAPACKAGE_URL="https://s3.amazonaws.com/${KNESSET_DATA_BUCKET}/${DATAPACKAGE_FILENAME}"
    fi

    if [ "${SLACK_LOG_WEBHOOK}" != "" ]; then
        echo "sending notification to slack"
        curl -X POST -g "${SLACK_LOG_WEBHOOK}" --data-urlencode 'payload={"channel": "#oknesset-travis", "username": "travis", "text": "'":sunglasses:\n datapackage: ${DATAPACKAGE_URL}\n Travis build: https://travis-ci.org/${TRAVIS_REPO_SLUG}/builds/${TRAVIS_BUILD_ID}"'"}'
    else
        echo "skipping slack integration because missing relevant slack tokens"
    fi
else
    echo "skipping buildling datapackage and slack notification because branch is not in datapackage branches"
fi
