variable "account_name" {}
variable "fhir_api_image" {}
variable "fhir_api_migration_image" {}
variable "fhir_api_port" {
  default = 8000
}
variable "redirect_to_strategy_page" {}
variable "private_load_balancer" { default = true }
variable "ecs_cluster_id" {}
variable "desired_task_count" {}
variable "db" {
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
variable "require_authentication" { default = "True" }
