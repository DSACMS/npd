variable "account-name" {}
variable "fhir-db" {
  type = object({
    db_instance_master_user_secret_arn = string
    db_instance_address                = string
    db_instance_name                   = string
    db_instance_port                   = string
  })
}
variable "etl-db" {
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
    alb_security_group_id = string
    api_security_group_id = string
    vpc_id                = string
  })
}