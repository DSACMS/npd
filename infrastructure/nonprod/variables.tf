variable "region" {
  default = "us-east-1"
}

variable "tier" {
  default = "dev"
}

variable "vpc_id" {
  default = "vpc-05bd23d8f48e88a4f"
}

variable "migration_image" { default = "public.ecr.aws/docker/library/hello-world:nanoserver-ltsc2022" }
variable "fhir_api_image" { default = "public.ecr.aws/docker/library/hello-world:nanoserver-ltsc2022" }