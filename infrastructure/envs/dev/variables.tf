variable "region" {
  default = "us-east-1"
}

variable "tier" {
  default = "dev"
}

variable "migration_image" { default = "575012135727.dkr.ecr.us-east-1.amazonaws.com/npd-east-dev-fhir-api-migrations:latest" }
variable "fhir_api_image" { default = "575012135727.dkr.ecr.us-east-1.amazonaws.com/npd-east-dev-fhir-api@sha256:d63a97d317feff204266a9655daa425377cab5832127e47076ca1ce91950d296" }
