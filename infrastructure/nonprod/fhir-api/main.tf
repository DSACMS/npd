terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.99.1"
    }
  }
}

data "aws_region" "current" {}
data "aws_partition" "current" {}
data "aws_caller_identity" "current" {}

## ECR Repositories
resource "aws_ecr_repository" "fhir_api" {
  name = "${var.account_name}-fhir-api"
}

resource "aws_ecr_repository" "fhir_api_migrations" {
  name = "${var.account_name}-fhir-api-migrations"
}

## ECS Roles and Policies

resource "aws_iam_role" "fhir_api_role" {
  name = "${var.account_name}-fhir-api-role"
  description = "Defines what AWS actions the FHIR API task is allowed to make"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_policy" "fhir_api_can_access_fhir_api_db_secret" {
  name = "${var.account_name}-fhir-api-can-access-fhir-database-secret"
  description = "Allows ECS to access the RDS secret"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "secretsmanager:GetSecretValue",
        Effect = "Allow"
        Resource = [
          var.db.db_instance_master_user_secret_arn,
          aws_secretsmanager_secret.django_secret.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "fhir_api_can_access_database_secret_attachment" {
  role = aws_iam_role.fhir_api_role.name
  policy_arn = aws_iam_policy.fhir_api_can_access_fhir_api_db_secret.arn
}

resource "aws_iam_policy" "fhir_api_logs_policy" {
  name        = "${var.account_name}-fhir-api-can-log-to-cloudwatch"
  description = "Allow ECS tasks to write logs to CloudWatch"
  path        = "/delegatedadmin/developer/"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "arn:${data.aws_partition.current.partition}:logs:*:${data.aws_caller_identity.current.account_id}:log-group:/ecs/${var.account_name}*:*"
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "fhir_api_can_create_cloudwatch_logs" {
  policy_arn = aws_iam_policy.fhir_api_logs_policy.id
  role       = aws_iam_role.fhir_api_role.id
}

## FHIR API Configuration

data "aws_secretsmanager_random_password" "django_secret_value" {
  password_length = 20
}

resource "aws_secretsmanager_secret" "django_secret" {
  name_prefix = "${var.account_name}-fhir-api-django-secret"
  description = "Secret value to use with the Django application"
}

resource "aws_secretsmanager_secret_version" "django_secret_version" {
  secret_id = aws_secretsmanager_secret.django_secret.id
  secret_string_wo = data.aws_secretsmanager_random_password.django_secret_value.random_password
  secret_string_wo_version = 1
}

resource "aws_ecs_task_definition" "app" {
  family                   = "${var.account_name}-fhir-api-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.fhir_api_role.arn

  container_definitions = jsonencode([
    # In the past, I've put the migration container in a separate task and invoked it manually to avoid the case
    # where we have (for example) 4 API containers and 4 flyway containers and the 4 flyway containers all try to update
    # the database at once. Flyway looks like it uses a Postgres advisory lock to solve this
    # (https://documentation.red-gate.com/fd/flyway-postgresql-transactional-lock-setting-277579114.html).
    # If we have problems, we can pull this container definition into it's own task and schedule it to run before new
    # API containers are deployed
    {
      name      = "${var.account_name}-fhir-api-migration"
      image     = var.fhir_api_migration_image
      essential = false
      command = [ "migrate" ]
      environment = [
        {
          name = "FLYWAY_URL"
          value = "jdbc:postgresql://${var.db.db_instance_address}:${var.db.db_instance_port}/${var.app_db_name}"
        }
      ],
      secrets = [
        {
          name      = "FLYWAY_USER"
          valueFrom = "${var.account_name}:username::"
        },
        {
          name      = "FLYWAY_PASSWORD"
          valueFrom = "${var.db.db_instance_master_user_secret_arn}:password::"
        },
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${var.account_name}-fhir-api-migration-logs"
          "awslogs-region"        = data.aws_region.current.name
          "awslogs-stream-prefix" = "${var.account_name}-fhir-api-migration-logs"
        }
      }
    },
    {
      name      = "${var.account_name}-fhir-api",
      image     = var.fhir_api_image
      essential = true
      environment  = [
        {
          name  = "NPD_DB_NAME"
          value = var.app_db_name
        },
        {
          name  = "NPD_DB_HOST"
          value = var.db.db_instance_address
        },
        {
          name  = "NPD_DB_PORT"
          value = tostring(var.db.db_instance_port)
        },
        {
          name  = "NPD_DB_ENGINE"
          value = "django.db.backends.postgresql"
        },
        {
          name = "DEBUG"
          value = ""
        },
        {
          name  = "DJANGO_ALLOWED_HOSTS"
          value = var.allowed_hosts
        },
        {
          name  = "DJANGO_LOGLEVEL"
          value = "WARNING"
        },
        {
          name  = "NPD_PROJECT_NAME"
          value = "ndh"
        },
        {
          name = "CACHE_LOCATION",
          value = ""
        }
      ]
      secrets = [
        {
          name      = "NPD_DJANGO_SECRET"
          valuefrom = aws_secretsmanager_secret_version.django_secret_version.arn
        },
        {
          name      = "NPD_DB_USER"
          valueFrom = "${var.db.db_instance_master_user_secret_arn}:username::"
        },
        {
          name      = "NPD_DB_PASSWORD"
          valueFrom = "${var.db.db_instance_master_user_secret_arn}:password::"
        },
      ]
      portMappings = [{ containerPort = 8000 }]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${var.account_name}-fhir-api-logs"
          "awslogs-region"        = data.aws_region.current.name
          "awslogs-stream-prefix" = "${var.account_name}-fhir-api-logs"
        }
      }
      #   TODO: Implement for your app
      #   healthCheck = {
      #     command     = []
      #     interval    = 10
      #     timeout     = 5
      #     retries     = 10
      #     startPeriod = 30
      #   }
    }
  ])
}
