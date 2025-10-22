output "api_alb_dns_name" {
  value = module.fhir-api.api_alb_dns_name
}

output "api_db_instance_endpoint" {
  value = module.api-db.db_instance_endpoint
}

output "etl_db_instance_endpoint" {
  value = module.etl-db.db_instance_endpoint
}

output "api_ecr_repository_name" {
  value = module.fhir-api.api_ecr_repository_name
}

output "api_migrations_ecr_repository_name" {
  value = module.fhir-api.api_migrations_ecr_repository_name
}
