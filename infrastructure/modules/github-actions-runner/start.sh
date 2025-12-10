#!/bin/bash
set -euo pipefail

check_env() {
    if [ -z "${GITHUB_ORG:-}" ]; then
        echo "Env variable GITHUB_ORG is required but not set"
        exit 1
    fi

    if [ -z "${GITHUB_RUNNER_TOKEN:-}" ]; then
        echo "Env variable GITHUB_RUNNER_TOKEN is required but not set"
        exit 1
    fi

    if [ -z "${ENV_LABEL:-}" ]; then
        echo "Env variable ENV_LABEL is required but not set"
        exit 1
    fi
}

register_runner() {
    ./config.sh --unattended --url https://github.com/$GITHUB_ORG --token $GITHUB_RUNNER_TOKEN --labels experimental,$ENV_LABEL
}

check_env
register_runner
./run.sh