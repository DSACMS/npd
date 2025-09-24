output "db_instance_endpoint" {
  description = "The connection endpoint"
  value       = module.rds.db_instance_endpoint
}

output "alb_dns_name" {
  description = "The DNS name for the application load balancer"
  value       = aws_lb.alb.dns_name
}

output "frontend_s3_bucket_website" {
  description = "The S3 bucket website endpoint hosting the frontend"
  value       = aws_s3_bucket_website_configuration.frontend_bucket_website_configuration.website_endpoint
}

output "frontend_s3_bucket" {
  description = "The S3 bucket hosting the frontend"
  value       = aws_s3_bucket.frontend_bucket.bucket
}

