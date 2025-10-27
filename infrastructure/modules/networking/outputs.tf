output "db_security_group_id" {
  description = "A list of security group IDs for use with the databases"
  value       = aws_security_group.fhir_api_db_sg.id
}

output "etl_db_security_group_id" {
  description = "A list of security group IDs for use with the databases"
  value       = aws_security_group.fhir_etl_db_sg.id
}

output "private_subnet_ids" {
  description = "The private subnets used for the API"
  value       = data.aws_subnets.private_subnets.ids
}

output "private_subnet_group_name" {
  description = "The name of the subnet group used with the databases"
  value       = aws_db_subnet_group.private_subnets.name
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = data.aws_subnets.public_subnets.ids
}

output "api_security_group_id" {
  description = "The security group for the FHIR API"
  value       = aws_security_group.fhir_api_sg.id
}

output "alb_security_group_id" {
  description = "The security group for the load balancer"
  value       = aws_security_group.fhir_api_alb_sg.id
}

output "etl_alb_security_group_id" {
  description = "The security group for the Dagster UI load balancer"
  value       = aws_security_group.etl_webserver_alb_sg.id
}

output "etl_security_group_id" {
  description = "The security group for the Dagster processes"
  value       = aws_security_group.etl_sg.id
}

output "vpc_id" {
  value = var.vpc_id
}
