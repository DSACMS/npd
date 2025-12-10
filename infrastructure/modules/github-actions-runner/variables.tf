variable "account_name" {}
variable "tier" {}
variable "subnet_ids" {}
variable "security_group_ids" {}
variable "github_runner_image" {}
variable "ecs_cluster_id" {}
variable "enable_containerized_runner" {
  default = false
}
variable "enable_preconfigured_ec2_instance" {
  default = false
}