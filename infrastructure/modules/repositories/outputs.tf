output "fhir_api_repository_name" {
  value = aws_ecr_repository.fhir_api.name
}

output "fhir_api_migrations_repository_name" {
  value = aws_ecr_repository.fhir_api_migrations.name
}

output "dagster_repository_name" {
  value = aws_ecr_repository.dagster.name
}
