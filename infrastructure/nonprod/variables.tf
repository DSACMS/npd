variable "region" {
  default = "us-east-1"
}

variable "tier" {
  default = "dev"
}

variable "migration_image" { default = "public.ecr.aws/docker/library/hello-world:nanoserver-ltsc2022" }
variable "fhir_api_image" { default = "public.ecr.aws/docker/library/hello-world:nanoserver-ltsc2022" }
variable "dagster_image" { default = "public.ecr.aws/docker/library/hello-world:nanoserver-ltsc2022" }