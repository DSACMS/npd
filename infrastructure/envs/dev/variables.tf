variable "region" {
  default = "us-east-1"
}

variable "tier" {
  default = "dev"
}

variable "migration_image" { default = "575012135727.dkr.ecr.us-east-1.amazonaws.com/npd-east-dev-fhir-api-migrations:latest" }
variable "fhir_api_image" { default = "575012135727.dkr.ecr.us-east-1.amazonaws.com/npd-east-dev-fhir-api:latest" }
variable "dagster_image" { default = "575012135727.dkr.ecr.us-east-1.amazonaws.com/npd-east-dev-dagster:latest" }
variable "github_runner_image" { default = "575012135727.dkr.ecr.us-east-1.amazonaws.com/npd-east-dev-dagster:latest" }
variable "require_authentication" { default = "True" }
