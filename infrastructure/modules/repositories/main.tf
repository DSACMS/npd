resource "aws_ecr_repository" "fhir_api" {
  name = "${var.account_name}-fhir-api"
  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "fhir_api_migrations" {
  name = "${var.account_name}-fhir-api-migrations"
  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "dagster" {
  name = "${var.account_name}-dagster"
  image_scanning_configuration {
    scan_on_push = true
  }
}
