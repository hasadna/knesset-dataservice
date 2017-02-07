#!/usr/bin/env bash

set -e  # exit on errors

[ -f .travis/.env ] && source .travis/.env

### functions ###

travis_build_url() {
    echo "https://travis-ci.org/${TRAVIS_REPO_SLUG}/builds/${TRAVIS_BUILD_ID}"
}

travis_metadata() {
    echo "REPO_SLUG=${TRAVIS_REPO_SLUG} BRANCH=${TRAVIS_BRANCH} BUILD_NUMBER=${TRAVIS_BUILD_NUMBER} BUILD_ID=${TRAVIS_BUILD_ID}"
}

send_slack_notification() {
    local msg="${1}"
    echo "sending notification to slack: '${msg}'"
    if [ "${SLACK_LOG_WEBHOOK}" != "" ]; then
        if curl -X POST -g "${SLACK_LOG_WEBHOOK}" --data-urlencode 'payload={"channel": "#oknesset-travis", "username": "travis", "text": "'"${msg}"'"}'; then
            echo "OK"
            return 0
        else
            echo "error sending slack notification"
            return 1
        fi
    else
        echo "skipping slack integration because missing relevant slack tokens"
        return 2
    fi
}

upload_datapackage() {
    local src="${1}"
    local dst="${2}"
    if [ "${AWS_ACCESS_KEY_ID}" != "" ] && [ "${AWS_SECRET_ACCESS_KEY}" != "" ]; then
        echo "uploading '${src}' to S3: '${dst}'"
        if ! which aws; then
            pip install awscli
        fi
        if aws s3 cp "${src}" "s3://${dst}" --acl=public-read; then
            echo "OK"
            return 0
        else
            echo "error uploading to S3"
            return 1
        fi
    else
        echo "skipping datapackage upload because missing aws environment vars"
        return 2
    fi
}

make_datapackage() {
    if [[ "${BUILD_DATAPACKAGE_BRANCHES}" == *"${TRAVIS_BRANCH}"* ]]; then
        mkdir -p data
        if [ "${DATAPACKAGE_SSH_PROXY_KEY}" != "" ]; then
            pushd python > /dev/null
                echo "making datapackage for last ${DATAPACKAGE_LAST_DAYS} days"
                bin/make_datapackage.py --days "${DATAPACKAGE_LAST_DAYS}" --debug --zip --http-proxy "socks5://localhost:8123"
                local make_datapackage_result=$?
            popd > /dev/null
            if [ $make_datapackage_result == 0 ]; then
                echo "OK"
                return 0
            else
                echo "failed to create datapackage"
                return 1
            fi
        else
            echo "skipping datapackage creation because missing ssh proxy"
            return 2
        fi
    else
        echo "skipping datapackage creation because branch is not in datapackage branches"
        return 2
    fi
}

run_tests() {
    echo "Running python tests"
    pushd python > /dev/null
        if ! bin/run_tests.sh; then
            echo "Python tests failed"
            return 1
        fi
    popd > /dev/null
    echo "Running django tests"
    pushd django > /dev/null
        if ! ./manage.py test; then
            echo "Django tests failed"
            return 1
        fi
        echo "Test django migrations"
        if ! ./manage.py syncdb --noinput; then
            echo "Syncdb failed"
            return 1
        fi
        if ! ./manage.py migrate; then
            echo "migrate failed"
            return 1
        fi
    popd > /dev/null
    echo "OK"
    return 0
}

exit_error() {
    exit 1
}

exit_success() {
    if [ "${DATAPACKAGE_URL}" != "" ]; then
        if ! send_slack_notification ":sunglasses:\n datapackage: ${DATAPACKAGE_URL}\nTravis build: `travis_build_url`\n`travis_metadata`"; then
            exit_error
        else
            exit 0
        fi
    else
        exit 0
    fi
}


### main ###

if run_tests; then
    if make_datapackage; then
        DATAPACKAGE_FILENAME="datapackage_last_${DATAPACKAGE_LAST_DAYS}_days_`date "+%Y-%m-%d_%H-%M"`.zip"
        if upload_datapackage "data/datapackage.zip" "${KNESSET_DATA_BUCKET}/${DATAPACKAGE_FILENAME}"; then
            DATAPACKAGE_URL="https://s3.amazonaws.com/${KNESSET_DATA_BUCKET}/${DATAPACKAGE_FILENAME}"
        elif [ $? == 1 ]; then
            exit_error
        fi
    elif [ $? == 1 ]; then
        exit_error
    fi
else
    exit_error
fi

exit_success
