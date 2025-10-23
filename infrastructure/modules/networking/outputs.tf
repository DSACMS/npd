output "db_security_group_id" {
  description = "A list of security group IDs for use with the databases"
  value       = aws_security_group.fhir_api_db_sg.id
}

output "db_subnet_group_name" {
  description = "The name of the subnet group used with the databases"
  value       = aws_db_subnet_group.database_subnets.name
}

output "api_security_group_id" {
  description = "The security group for the FHIR API"
  value       = aws_security_group.fhir_api_sg.id
}

output "alb_security_group_id" {
  description = "The security group for the load balancer"
  value       = aws_security_group.fhir_api_alb_sg.id
}

output "db_subnet_ids" {
  description = "The private subnets used for the API"
  value       = data.aws_subnets.database_subnets.ids
}

output "etl_subnet_ids" {
  description = "The private subnets used for the ETL processes"
  value       = data.aws_subnets.etl_subnets.ids
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = data.aws_subnets.public_subnets.ids
}

output "vpc_id" {
  value = var.vpc_id
}