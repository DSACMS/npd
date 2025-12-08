DEPLOYED_VERSION=$(
aws ecs describe-task-definition \
  --task-definition $(aws ecs describe-services \
    --cluster "npd-east-dev-ecs-cluster" \
    --services "npd-east-dev-fhir-api-service" \
    --query "services[0].taskDefinition" \
    --output text) \
  --query "taskDefinition.containerDefinitions[0].image" \
  --output text \
  | awk -F: '{print $NF}'
)

echo $DEPLOYED_VERSION
