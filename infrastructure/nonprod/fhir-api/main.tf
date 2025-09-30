## ECR Repositories
resource "aws_ecr_repository" "fhir_api" {
  name = "${var.account_name}-fhir-api"
}

resource "aws_ecr_repository" "fhir_api_migrations" {
  name = "${var.account_name}-fhir-api-migrations"
}

## ECS Task Definition