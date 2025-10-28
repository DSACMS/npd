variable "region" {
  default = "us-east-1"
}

variable "tier" {
  default = "prod"
}

variable "migration_image" { default = "596240962403.dkr.ecr.us-east-1.amazonaws.com/npd-east-prod-fhir-api-migrations:latest" }
variable "fhir_api_image" { default = "596240962403.dkr.ecr.us-east-1.amazonaws.com/npd-east-prod-fhir-api:latest" }
variable "dagster_image" { default = "596240962403.dkr.ecr.us-east-1.amazonaws.com/npd-east-dev-dagster:latest" }
variable "redirect_to_strategy_page" { default = true }
variable "fhir_api_private_load_balancer" { default = false }
