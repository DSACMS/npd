variable "account_name" {}
variable "tier" {}
variable "subnet_ids" {}
variable "security_group_ids" {}
variable "enable_preconfigured_ec2_instance" {
  default = false
}