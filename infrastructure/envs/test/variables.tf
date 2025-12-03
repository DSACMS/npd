variable "region" {
  default = "us-east-1"
}

variable "tier" {
  default = "test"
}

variable "migration_image" { default = "575012135727.dkr.ecr.us-east-1.amazonaws.com/npd-east-test-fhir-api-migrations:latest" }
variable "fhir_api_image" { default = "575012135727.dkr.ecr.us-east-1.amazonaws.com/npd-east-test-fhir-api:latest" }
variable "dagster_image" { default = "575012135727.dkr.ecr.us-east-1.amazonaws.com/npd-east-test-dagster:latest" }
variable "fhir_api_private_load_balancer" { default = true }
variable "require_authentication" { default = "True" }
