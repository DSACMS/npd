variable "region" {
  default = "us-east-1"
}

variable "tier" {
  default = "prod"
}

variable "migration_image" { default = "596240962403.dkr.ecr.us-east-1.amazonaws.com/npd-east-prod-fhir-api-migrations:latest" }
variable "fhir_api_image" { default = "596240962403.dkr.ecr.us-east-1.amazonaws.com/npd-east-prod-fhir-api:latest" }
variable "redirect_to_strategy_page" { default = true }
