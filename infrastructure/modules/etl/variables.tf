variable "account_name" {}
variable "dagster_home" { default = "/opt/dagster/dagster_home" }
variable "dagster_image" {}
variable "fhir_api_migration_image" {}
variable "ecs_cluster_id" {}
variable "npd_sync_task_arn" {}
variable "db" {
  type = object({
    db_instance_master_user_secret_arn = string
    db_instance_address                = string
    db_instance_port                   = string
    db_instance_name                   = string
  })
}
variable "networking" {
  type = object({
    public_subnet_ids         = list(string)
    private_subnet_ids        = list(string)
    etl_security_group_id     = string
    etl_alb_security_group_id = string
    vpc_id                    = string
  })
}