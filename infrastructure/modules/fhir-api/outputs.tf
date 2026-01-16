output "api_alb_dns_name" {
  value = aws_lb.fhir_api_alb.dns_name
}

output "api_dot_alb_dns_name" {
  value = aws_alb.fhir_api_alb_redirect.dns_name
}

output "api_alb_zone_id" {
  value = aws_lb.fhir_api_alb.zone_id
}