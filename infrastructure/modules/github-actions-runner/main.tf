data "aws_caller_identity" "current" {}

locals {
  account_id = data.aws_caller_identity.current.account_id
}

resource "aws_iam_role" "github_runner_resource_creation_role" {
  description = "Role to be assumed for resource creation"
  name        = "${var.account_name}-github-actions-runner-creation-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
        }
        StringLike = {
          "token.actions.githubusercontent.com:sub" = "repo:CMS-Enterprise/NPD:*"
        }
      }
      Principal = {
        Federated = "arn:aws:iam::${local.account_id}:oidc-provider/token.actions.githubusercontent.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "github_runner_has_admin" {
  role       = aws_iam_role.github_runner_resource_creation_role.id
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

resource "aws_iam_role_policy_attachment" "github_runner_has_ado_restriction" {
  role       = aws_iam_role.github_runner_resource_creation_role.id
  policy_arn = "arn:aws:iam::${local.account_id}:policy/ADO-Restriction-Policy"
}

resource "aws_iam_role_policy_attachment" "github_runner_has_region_restriction" {
  role       = aws_iam_role.github_runner_resource_creation_role.id
  policy_arn = "arn:aws:iam::${local.account_id}:policy/CMSCloudApprovedRegions"
}

resource "aws_iam_role_policy_attachment" "github_runner_has_user_creation_restriction" {
  role       = aws_iam_role.github_runner_resource_creation_role.id
  policy_arn = "arn:aws:iam::${local.account_id}:policy/ct-iamCreateUserRestrictionPolicy"
}

resource "aws_instance" "github_actions_instance" {
  ami                    = "ami-04345af6ff8317b5e"
  instance_type          = "m5.xlarge"
  vpc_security_group_ids = var.security_group_ids
  subnet_id              = var.subnet_id
  iam_instance_profile   = "cms-cloud-base-ec2-profile-v4"
  root_block_device {
    volume_size = 100
  }
  tags = {
    Name = "github-actions-runner-instance"
  }
}

### A GitHub Actions Runner ECS

resource "aws_cloudwatch_log_group" "github_runner_log_group" {
  name              = "/custom/${var.account_name}-github-runner-logs"
  retention_in_days = 30
}

resource "aws_ecr_repository" "github_actions_runner" {
  name = "${var.account_name}-github-actions-runner"
  image_scanning_configuration {
    scan_on_push = true
  }
}

data "aws_secretsmanager_random_password" "github_pat_random" {
  password_length = 20
}

resource "aws_secretsmanager_secret" "github_pat" {
  name_prefix = "${var.account_name}-github-pat"
  description = "GitHub Runner PAT"
}

resource "aws_secretsmanager_secret_version" "github_pat_version" {
  secret_id                = aws_secretsmanager_secret.github_pat.id
  secret_string_wo         = data.aws_secretsmanager_random_password.github_pat_random.random_password
  secret_string_wo_version = 1
}

# ECS Roles and Policies
resource "aws_iam_role" "github_runner_execution_role" {
  name        = "${var.account_name}-github-runner-execution-role"
  description = "Defines what AWS actions the GitHub Runner task execution environment is allowed to make"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.github_runner_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_policy" "github_runner_can_access_github_pat_secret" {
  name        = "${var.account_name}-github-runner-can-access-github-pat-secret"
  description = "Allows ECS to access the GitHub PAT secret"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "secretsmanager:GetSecretValue",
        Effect = "Allow"
        Resource = [
          aws_secretsmanager_secret_version.github_pat_version.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "github_runner_can_access_github_pat_attachment" {
  role       = aws_iam_role.github_runner_execution_role.name
  policy_arn = aws_iam_policy.github_runner_can_access_github_pat_secret.arn
}

# FHIR API Task Configuration
resource "aws_ecs_task_definition" "github_actions_runner_task" {
  family                   = "${var.account_name}-github-actions-runner-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.github_runner_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "${var.account_name}-github-runner"
      image     = var.github_runner_image
      essential = false
      environment = [
        {
          name  = "GITHUB_ORG"
          value = "CMS-Enterprise/npd"
        },
      ]
      secrets = [
        {
          name      = "GITHUB_PAT"
          valueFrom = aws_secretsmanager_secret_version.github_pat_version.secret_string
        },
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.github_runner_log_group.name
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = var.account_name
        }
      }
    }
  ])
}

# API ECS Service
resource "aws_ecs_service" "app" {
  name            = "${var.account_name}-fhir-api-service"
  cluster         = var.ecs_cluster_id
  task_definition = aws_ecs_task_definition.github_actions_runner_task.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = var.security_group_ids
    assign_public_ip = false
  }
}