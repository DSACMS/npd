# Perms, Policies, and Roles
resource "aws_iam_role" "rotation_lambda_role" {
  name = "${var.account_name}-secrets-rotation-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.rotation_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_vpc_access" {
  role       = aws_iam_role.rotation_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_role_policy" "secrets_rotation_policy" {
  name = "${var.account_name}-secrets-rotation-policy"
  role = aws_iam_role.rotation_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:DescribeSecret",
          "secretsmanager:GetSecretValue",
          "secretsmanager:PutSecretValue",
          "secretsmanager:UpdateSecretVersionStage"
        ]
        Resource = var.secret_arn
      },
      {
        Effect   = "Allow"
        Action   = ["secretsmanager:GetRandomPassword"]
        Resource = "*"
      }
    ]
  })
}

# Lambda
resource "aws_lambda_function" "rotation" {
  function_name = "${var.account_name}-secrets-manager-postgres-rotation-lambda"
  description   = "Rotates a Secrets Manager secret for Amazon RDS PostgreSQL credentials using the single user rotation strategy."

  # AWS-managed S3 bucket containing the official rotation function code
  s3_bucket = "secrets-manager-rotation-apps-c0de1e0412b469545054417cc38af3c3"
  s3_key    = "SecretsManagerRDSPostgreSQLRotationSingleUser/SecretsManagerRDSPostgreSQLRotationSingleUser.zip"

  runtime     = "python3.10"
  handler     = "lambda_function.lambda_handler"
  timeout     = 30
  memory_size = 128

  role = aws_iam_role.rotation_lambda_role.arn

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = [var.security_group_id]
  }

  environment {
    variables = {
      SECRETS_MANAGER_ENDPOINT   = var.secrets_manager_endpoint
      EXCLUDE_CHARACTERS         = var.exclude_characters
      PASSWORD_LENGTH            = tostring(var.password_length)
      EXCLUDE_NUMBERS            = var.exclude_numbers
      EXCLUDE_PUNCTUATION        = var.exclude_punctuation
      EXCLUDE_UPPERCASE          = var.exclude_uppercase
      EXCLUDE_LOWERCASE          = var.exclude_lowercase
      REQUIRE_EACH_INCLUDED_TYPE = var.require_each_included_type
    }
  }

  lifecycle {
    ignore_changes = [
      source_code_hash,
    ]
  }
}

# Lambda Permission
resource "aws_lambda_permission" "allow_secrets_manager" {
  statement_id  = "AllowSecretsManagerInvocation"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.rotation.function_name
  principal     = "secretsmanager.amazonaws.com"
}

# Secrets Manager Rotation Configuration
resource "aws_secretsmanager_secret_rotation" "rotation" {
  secret_id           = var.secret_arn
  rotation_lambda_arn = aws_lambda_function.rotation.arn

  rotation_rules {
    automatically_after_days = var.rotation_days
  }
}