#!/usr/bin/env bash

[ -f .travis/.env ] && source .travis/.env

### constants ###

OK=0
FAILED=1
SKIPPED=2

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
        if [ "${DATAPACKAGE_SSH_PROXY_KEY}" != "" ] && [ "${DATAPACKAGE_SSH_PROXY_HOST}" != "" ]; then
            echo "creating ssh socks tunnel"
            echo -e "${DATAPACKAGE_SSH_PROXY_KEY}" > sshproxy.key
            chmod 400 sshproxy.key
            ssh -o StrictHostKeyChecking=no -D 8123 -C -f -N -i sshproxy.key "${DATAPACKAGE_SSH_PROXY_HOST}"
            pushd python > /dev/null
                echo "making datapackage for last ${DATAPACKAGE_LAST_DAYS} days"
                bin/make_datapackage.py --days "${DATAPACKAGE_LAST_DAYS}" --debug --zip --http-proxy "socks5://localhost:8123"
                local make_datapackage_result=$?
            popd > /dev/null
            if [ $make_datapackage_result == 0 ]; then
                echo "OK"
                echo "killing the ssh tunnel"
                pkill -fe -9 sshproxy
                return 0
            else
                echo "failed to create datapackage"
                return 1
            fi
        else
            echo "skipping datapackage creation because missing ssh proxy variables"
            return 2
        fi
    else
        echo "skipping datapackage creation because branch is not in datapackage branches"
        return 2
    fi
}

run_tests() {
    echo "running tests"
    pushd python > /dev/null
        bin/run_tests.sh
        local run_tests_result=$?
    popd > /dev/null
    if [ $run_tests_result == 0 ]; then
        echo "OK"
        return 0
    else
        echo "tests failed"
        return 1
    fi
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
    make_datapackage
    case $? in
        $OK)
            DATAPACKAGE_FILENAME="datapackage_last_${DATAPACKAGE_LAST_DAYS}_days_`date "+%Y-%m-%d_%H-%M"`.zip"
            upload_datapackage "data/datapackage.zip" "${DATAPACKAGE_FILENAME}"
            case $? in
                $OK)
                    DATAPACKAGE_URL="https://s3.amazonaws.com/${KNESSET_DATA_BUCKET}/${DATAPACKAGE_FILENAME}"
                    ;;
                $FAILED)
                    exit_error
                    ;;
                $SKIPPED)
                    true
                    ;;
            esac
            ;;
        $FAILED)
            exit_error
            ;;
        $SKIPPED)
            true
            ;;
    esac
    exit_success
else
    exit_error
fi
