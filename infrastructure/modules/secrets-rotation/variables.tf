variable "account_name" {
  description = "Account name prefix for resource naming"
  type        = string
}

variable "secret_arn" {
  description = "ARN of the secret to rotate"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where the Lambda runs"
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs for the Lambda"
  type        = list(string)
}

variable "security_group_id" {
  description = "Security group ID for the Lambda"
  type        = string
}

variable "rotation_days" {
  description = "Number of days between automatic rotations"
  type        = number
  default     = 7
}

variable "secrets_manager_endpoint" {
  description = "Secrets Manager endpoint URL"
  type        = string
  default     = "https://secretsmanager.us-east-1.amazonaws.com"
}

variable "password_length" {
  description = "Length of generated passwords"
  type        = number
  default     = 32
}

variable "exclude_characters" {
  description = "Characters to exclude from generated passwords"
  type        = string
  default     = ":/@\"'\\"
}

variable "exclude_numbers" {
  description = "Whether to exclude numbers from passwords"
  type        = string
  default     = "false"
}

variable "exclude_punctuation" {
  description = "Whether to exclude punctuation from passwords"
  type        = string
  default     = "false"
}

variable "exclude_uppercase" {
  description = "Whether to exclude uppercase letters from passwords"
  type        = string
  default     = "false"
}

variable "exclude_lowercase" {
  description = "Whether to exclude lowercase letters from passwords"
  type        = string
  default     = "false"
}

variable "require_each_included_type" {
  description = "Require at least one of each included character type"
  type        = string
  default     = "true"
}