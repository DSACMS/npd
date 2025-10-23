output "api_alb_dns_name" {
  value = aws_lb.fhir_api_alb.dns_name
}

output "api_ecr_repository_name" {
  value = aws_ecr_repository.fhir_api.name
}

output "api_migrations_ecr_repository_name" {
  value = aws_ecr_repository.fhir_api_migrations.name
}
