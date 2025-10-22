output "api_alb_dns_name" {
  value = module.fhir-api.api_alb_dns_name
}

output "api_db_instance_endpoint" {
  value = module.api-db.db_instance_endpoint
}

output "etl_db_instance_endpoint" {
  value = module.etl-db.db_instance_endpoint
}

output "fhir_api_repository_name" {
  value = module.repositories.fhir_api_repository_name
}

output "fhir_api_migrations_repository_name" {
  value = module.repositories.fhir_api_migrations_repository_name
}

output "dagster_repository_name" {
  value = module.repositories.dagster_repository_name
}