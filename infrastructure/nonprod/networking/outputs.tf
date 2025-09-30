output "db_security_group_id" {
  description = "A list of security group IDs for use with the databases"
  value = aws_security_group.fhir_api_db_sg.id
}

output "db_subnet_group_name" {
  description = "The name of the subnet group used with the databases"
  value = aws_db_subnet_group.database_subnets.name
}