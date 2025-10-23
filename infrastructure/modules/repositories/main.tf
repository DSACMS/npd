resource "aws_ecr_repository" "fhir_api" {
  name = "${var.account_name}-fhir-api"
}

resource "aws_ecr_repository" "fhir_api_migrations" {
  name = "${var.account_name}-fhir-api-migrations"
}

resource "aws_ecr_repository" "dagster" {
  name = "${var.account_name}-dagster"
}
