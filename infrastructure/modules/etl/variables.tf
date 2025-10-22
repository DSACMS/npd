variable "account_name" {}
variable "dagster_home" { default = "dagster_home" }
variable "dagster_image" {}
variable "ecs_cluster_id" {}
variable "db" {
  type = object({
    db_instance_master_user_secret_arn = string
    db_instance_address                = string
    db_instance_port                   = string
    db_instance_name = string
  })
}
variable "networking" {
  type = object({
    etl_subnet_ids = list(string)
    etl_security_group_id = string
    etl_alb_security_group_id = string
    public_subnet_ids     = list(string)
    vpc_id                = string
  })
}