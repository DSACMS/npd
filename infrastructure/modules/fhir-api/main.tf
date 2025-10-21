data "aws_region" "current" {}
data "aws_partition" "current" {}
data "aws_caller_identity" "current" {}

# ECR Repositories

resource "aws_ecr_repository" "fhir_api" {
  name = "${var.account_name}-fhir-api"
}

resource "aws_ecr_repository" "fhir_api_migrations" {
  name = "${var.account_name}-fhir-api-migrations"
}

# Log Groups

resource "aws_cloudwatch_log_group" "fhir_api_log_group" {
  name              = "/ecs/${var.account_name}-fhir-api-logs"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "fhir_api_migrations_log_group" {
  name              = "/ecs/${var.account_name}-fhir-api-migrations-logs"
  retention_in_days = 30
}

# ECS Roles and Policies
resource "aws_iam_role" "fhir_api_execution_role" {
  name        = "${var.account_name}-fhir-api-execution-role"
  description = "Defines what AWS actions the FHIR API task execution environment is allowed to make"
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
  role       = aws_iam_role.fhir_api_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_policy" "fhir_api_can_access_fhir_api_db_secret" {
  name        = "${var.account_name}-fhir-api-can-access-fhir-database-secret"
  description = "Allows ECS to access the RDS secret"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "secretsmanager:GetSecretValue",
        Effect = "Allow"
        Resource = [
          var.db.db_instance_master_user_secret_arn,
          aws_secretsmanager_secret_version.django_secret_version.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "fhir_api_can_access_database_secret_attachment" {
  role       = aws_iam_role.fhir_api_execution_role.name
  policy_arn = aws_iam_policy.fhir_api_can_access_fhir_api_db_secret.arn
}

resource "aws_iam_policy" "fhir_api_logs_policy" {
  name        = "${var.account_name}-fhir-api-can-log-to-cloudwatch"
  description = "Allow ECS tasks to write logs to CloudWatch"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect = "Allow"
        Resource = [
          "arn:${data.aws_partition.current.partition}:logs:*:${data.aws_caller_identity.current.account_id}:log-group:/ecs/${var.account_name}*:*"
        ]
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "fhir_api_can_create_cloudwatch_logs" {
  policy_arn = aws_iam_policy.fhir_api_logs_policy.id
  role       = aws_iam_role.fhir_api_execution_role.id
}

# FHIR API Secrets
data "aws_secretsmanager_random_password" "django_secret_value" {
  password_length = 20
}

resource "aws_secretsmanager_secret" "django_secret" {
  name_prefix = "${var.account_name}-fhir-api-django-secret"
  description = "Secret value to use with the Django application"
}

resource "aws_secretsmanager_secret_version" "django_secret_version" {
  secret_id                = aws_secretsmanager_secret.django_secret.id
  secret_string_wo         = data.aws_secretsmanager_random_password.django_secret_value.random_password
  secret_string_wo_version = 1
}

# FHIR API Task Configuration
resource "aws_ecs_task_definition" "app" {
  family                   = "${var.account_name}-fhir-api-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.fhir_api_execution_role.arn

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
      command   = ["migrate"]
      environment = [
        {
          name  = "FLYWAY_URL"
          value = "jdbc:postgresql://${var.db.db_instance_address}:${var.db.db_instance_port}/${var.db.db_instance_name}"
        }
      ],
      secrets = [
        {
          name      = "FLYWAY_USER"
          valueFrom = "${var.db.db_instance_master_user_secret_arn}:username::"
        },
        {
          name      = "FLYWAY_PASSWORD"
          valueFrom = "${var.db.db_instance_master_user_secret_arn}:password::"
        },
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.fhir_api_migrations_log_group.name
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = var.account_name
        }
      }
    },
    {
      name      = "${var.account_name}-fhir-api",
      image     = var.fhir_api_image
      essential = true
      environment = [
        {
          name  = "NPD_DB_NAME"
          value = var.db.db_instance_name
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
          name  = "DEBUG"
          value = ""
        },
        {
          name  = "DJANGO_ALLOWED_HOSTS"
          value = aws_lb.fhir_api_alb.dns_name
        },
        {
          name  = "DJANGO_LOGLEVEL"
          value = "WARNING"
        },
        {
          name  = "NPD_PROJECT_NAME"
          value = "npd"
        },
        {
          name  = "CACHE_LOCATION",
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
      portMappings = [{
        containerPort = var.fhir_api_port
      }]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.fhir_api_log_group.name
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = var.account_name
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

# API ECS Service
resource "aws_ecs_service" "app" {
  count = var.redirect_to_strategy_page == true ? 0 : 1
  name            = "${var.account_name}-fhir-api-service"
  cluster         = var.ecs_cluster_id
  task_definition = aws_ecs_task_definition.app.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    subnets          = var.networking.db_subnet_ids
    security_groups  = [var.networking.api_security_group_id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.fhir_api_tg[0].arn
    container_name   = "${var.account_name}-fhir-api"
    container_port   = var.fhir_api_port
  }
}

# API Load Balancer Configuration
resource "aws_lb" "fhir_api_alb" {
  name               = "${var.account_name}-fhir-api-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.networking.alb_security_group_id]
  subnets            = var.networking.public_subnet_ids
}

resource "aws_lb_target_group" "fhir_api_tg" {
  count = var.redirect_to_strategy_page ? 0 : 1
  name        = "${var.account_name}-fhir-api-tg"
  port        = var.fhir_api_port
  protocol    = "HTTP"
  vpc_id      = var.networking.vpc_id
  target_type = "ip"

  health_check {
    path                = "/fhir/healthCheck"
    port                = var.fhir_api_port
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 10
    matcher             = "200"
  }
}

resource "aws_lb_listener" "forward_to_task_group" {
  count = var.redirect_to_strategy_page ? 0 : 1
  load_balancer_arn = aws_lb.fhir_api_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.fhir_api_tg[1].arn
  }
}

resource "aws_lb_listener" "forward_to_strategy_page" {
  count = var.redirect_to_strategy_page ? 1 : 0
  load_balancer_arn = aws_lb.fhir_api_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "redirect"
    redirect {
      status_code = "HTTP_302"
      host = "www.cms.gov"
      path = "/priorities/health-technology-ecosystem/overview"
    }
  }
}
