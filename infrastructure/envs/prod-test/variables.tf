variable "region" {
  default = "us-east-1"
}

variable "tier" {
  default = "prod-test"
}

variable "migration_image" { default = "596240962403.dkr.ecr.us-east-1.amazonaws.com/npd-east-prod-test-fhir-api-migrations:latest" }
variable "fhir_api_image" { default = "596240962403.dkr.ecr.us-east-1.amazonaws.com/npd-east-prod-test-fhir-api:latest" }
variable "dagster_image" { default = "596240962403.dkr.ecr.us-east-1.amazonaws.com/npd-east-prod-test-dagster:latest" }
variable "redirect_to_strategy_page" { default = false }
variable "fhir_api_private_load_balancer" { default = true }
variable "require_authentication" { default = "True" }
