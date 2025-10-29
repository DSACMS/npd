#!/bin/bash
# Load environment specific .env
envname="${1:-sandbox}"

[ ! -f .env.$envname ] || export $(grep -v '^#' .env.$envname | xargs)

if [ -z "$CTKEY_USERNAME" ]; then
    read -p "Enter ctkey username: " CTKEY_USERNAME
fi

if [ -z "$CTKEY_PASSWORD" ]; then
    read -s -p "Enter password for $CTKEY_USERNAME: " CTKEY_PASSWORD
fi

function parse_and_write_ctkey_credentials() {
    local JSON=$1

    local aws_access_key_id=$(echo "$JSON" | jq -r .data.access_key)
    local aws_secret_access_key=$(echo "$JSON" | jq -r .data.secret_access_key)
    local aws_session_token=$(echo "$JSON" | jq -r .data.session_token)

    aws configure set aws_access_key_id "$aws_access_key_id" --profile $PROFILE_NAME
    aws configure set aws_secret_access_key "$aws_secret_access_key" --profile $PROFILE_NAME
    aws configure set aws_session_token "$aws_session_token" --profile $PROFILE_NAME
    aws configure set region "$AWS_REGION" --profile $PROFILE_NAME

    echo ""
    echo "Credentials set for profile $PROFILE_NAME, set the AWS_PROFILE environment variable to use with the AWS CLI"
}

CREDS_JSON=$(ctkey --username=$CTKEY_USERNAME --password=$CTKEY_PASSWORD --iam-role=$IAM_ROLE --account=$ACCOUNT_ID --url=https://cloudtamer.cms.gov --idms=2 viewjson)

parse_and_write_ctkey_credentials $CREDS_JSON
