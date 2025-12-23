output "rotation_lambda_arn" {
  description = "ARN of the rotation Lambda function"
  value       = aws_lambda_function.rotation.arn
}

output "rotation_lambda_role_arn" {
  description = "ARN of the IAM role used by the rotation Lambda"
  value       = aws_iam_role.rotation_lambda.arn
}

output "secret_arn" {
  description = "ARN of the managed secret"
  value       = aws_secretsmanager_secret.readonly_user.arn
}

output "secret_name" {
  description = "Name of the managed secret"
  value       = aws_secretsmanager_secret.readonly_user.name
}