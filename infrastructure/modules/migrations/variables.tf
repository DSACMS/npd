variable "account_name" {}
variable "region" {}
variable "tier" {}
variable "multi_az" {type = bool}

variable "fhir_db" {
  type = object({
    db_instance_master_user_secret_arn = string
    db_instance_address                = string
    db_instance_name                   = string
    db_instance_port                   = string
  })
}

variable "etl_db" {
  type = object({
    db_instance_master_user_secret_arn = string
    db_instance_address                = string
    db_instance_name                   = string
    db_instance_port                   = string
  })
}

variable "networking" {
  type = object({
    private_subnet_ids    = list(string)
    public_subnet_ids     = list(string)
    # alb_security_group_id = string
    # api_security_group_id = string
    vpc_id                = string
  })
}