output "lambda_function_arn" {
  description = "ARN of the rotation Lambda function"
  value       = aws_lambda_function.rotation.arn
}

output "lambda_function_name" {
  description = "Name of the rotation Lambda function"
  value       = aws_lambda_function.rotation.function_name
}

output "lambda_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = aws_iam_role.rotation_lambda_role.arn
}