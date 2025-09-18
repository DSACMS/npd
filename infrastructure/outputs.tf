output "db_instance_endpoint" {
  description = "The connection endpoint"
  value       = module.rds.db_instance_endpoint
}

output "alb_dns_name" {
  description = "The DNS name for the application load balancer"
  value       = aws_lb.alb.dns_name
}