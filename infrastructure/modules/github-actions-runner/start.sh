#!/bin/bash
set -euo pipefail

check_env() {
    if [ -z "${GITHUB_PAT:-}" ]; then
        echo "Env variable GITHUB_PAT is required but not set"
        exit 1
    fi

    if [ -z "${GITHUB_ORG:-}" ]; then
        echo "Env variable GITHUB_ORG is required but not set"
        exit 1
    fi
}

register_runner() {
    local github_token=$(curl -sL \
        -X POST \
        -H "Accept: application/vnd.github+json" \
        -H "Authorization: Bearer $GITHUB_PAT" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        https://api.github.com/orgs/$GITHUB_ORG/actions/runners/registration-token | jq -r .token)

    ./config.sh --unattended --url https://github.com/$GITHUB_ORG --token $github_token
}

check_env
register_runner
./run.sh