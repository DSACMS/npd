data "aws_region" "current" {}
data "aws_partition" "current" {}
data "aws_caller_identity" "current" {}

# Log Groups

resource "aws_cloudwatch_log_group" "fhir_api_log_group" {
  name              = "/custom/${var.account_name}-fhir-api-logs/#_json"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "fhir_api_migrations_log_group" {
  name              = "/custom/${var.account_name}-fhir-api-migrations-logs/#_json"
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
          aws_secretsmanager_secret_version.django_secret_version.arn,
          aws_secretsmanager_secret_version.fhir_api_superuser_default_password_version.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "fhir_api_can_access_database_secret_attachment" {
  role       = aws_iam_role.fhir_api_execution_role.name
  policy_arn = aws_iam_policy.fhir_api_can_access_fhir_api_db_secret.arn
}

data "aws_secretsmanager_random_password" "fhir_api_superuser_default_password_value" {
  password_length = 20
}

resource "aws_secretsmanager_secret" "fhir_api_superuser_default_password" {
  name_prefix = "${var.account_name}-fhir-api-superuser-default-password"
  description = "Initial FHIR API superuser account password"
}

data "external" "fhir_api_superuser_default_password_hash" {
  program = ["python3", "${path.module}/generate_hash.py"]

  query = {
    password_input = data.aws_secretsmanager_random_password.fhir_api_superuser_default_password_value.random_password
  }
}

resource "aws_secretsmanager_secret_version" "fhir_api_superuser_default_password_version" {
  secret_id = aws_secretsmanager_secret.fhir_api_superuser_default_password.id
  secret_string_wo = jsonencode({
    password        = data.aws_secretsmanager_random_password.fhir_api_superuser_default_password_value.random_password
    hashed_password = data.external.fhir_api_superuser_default_password_hash.result.hashed_password
  })
  secret_string_wo_version = 1
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
      command   = ["migrate", "-outputType=json"]
      environment = [
        {
          name  = "FLYWAY_URL"
          value = "jdbc:postgresql://${var.db.db_instance_address}:${var.db.db_instance_port}/${var.db.db_instance_name}"
        },
        {
          name  = "FLYWAY_PLACEHOLDERS_apiSchema"
          value = var.db.db_instance_name
        },
      ]
      secrets = [
        {
          name      = "FLYWAY_USER"
          valueFrom = "${var.db.db_instance_master_user_secret_arn}:username::"
        },
        {
          name      = "FLYWAY_PASSWORD"
          valueFrom = "${var.db.db_instance_master_user_secret_arn}:password::"
        },
        {
          name      = "FLYWAY_PLACEHOLDERS_superuserDefaultPassword"
          valueFrom = "${aws_secretsmanager_secret_version.fhir_api_superuser_default_password_version.arn}:hashed_password::"
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
          value = jsonencode([aws_lb.fhir_api_alb.dns_name, var.networking.api_domain, var.networking.directory_domain])
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
        },
        {
          name  = "NPD_REQUIRE_AUTHENTICATION",
          value = var.require_authentication
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
  name            = "${var.account_name}-fhir-api-service"
  cluster         = var.ecs_cluster_id
  task_definition = aws_ecs_task_definition.app.arn
  launch_type     = "FARGATE"
  desired_count   = var.desired_task_count

  network_configuration {
    subnets          = var.networking.private_subnet_ids
    security_groups  = [var.networking.api_security_group_id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.fhir_api_tg.arn
    container_name   = "${var.account_name}-fhir-api"
    container_port   = var.fhir_api_port
  }
}

# ALB directory.cms.gov traffic

resource "aws_lb" "fhir_api_alb" {
  name               = "${var.account_name}-fhir-api-alb"
  internal           = var.private_load_balancer
  load_balancer_type = "application"
  security_groups    = [var.networking.alb_security_group_id]
  subnets            = var.networking.public_subnet_ids
}

resource "aws_lb_target_group" "fhir_api_tg" {
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

# Port 80 traffic
# TODO: upgrade all incoming traffic to HTTPS after:
# - internal domain names are registered
# - ssl certs are requested and validated

resource "aws_lb_listener" "forward_to_task_group" {
  count             = var.redirect_to_strategy_page ? 0 : 1
  load_balancer_arn = aws_lb.fhir_api_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.fhir_api_tg.arn
  }
}

resource "aws_lb_listener" "forward_to_strategy_page" {
  count             = var.redirect_to_strategy_page ? 1 : 0
  load_balancer_arn = aws_lb.fhir_api_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      status_code = "HTTP_302"
      host        = "www.cms.gov"
      path        = "/priorities/health-technology-ecosystem/overview"
    }
  }
}

resource "aws_lb_listener_rule" "preview_flag" {
  count        = var.redirect_to_strategy_page ? 1 : 0
  listener_arn = aws_lb_listener.forward_to_strategy_page[0].arn

  condition {
    query_string {
      key   = "preview"
      value = "true"
    }
  }

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.fhir_api_tg.arn
  }
}

# Port 443 Traffic
# TODO: upgrade all incoming traffic to HTTPS after:
# - internal domain names are registered
# - ssl certs are requested and validated

data "aws_acm_certificate" "directory_ssl_cert" {
  count    = var.networking.enable_ssl_directory ? 1 : 0
  domain   = var.networking.directory_domain
  statuses = ["ISSUED"]
}

resource "aws_lb_listener" "forward_to_task_group_https" {
  count             = var.redirect_to_strategy_page && var.networking.enable_ssl_directory ? 0 : 1
  load_balancer_arn = aws_lb.fhir_api_alb.arn
  port              = 443
  protocol          = "HTTPS"
  certificate_arn   = data.aws_acm_certificate.directory_ssl_cert[0].arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.fhir_api_tg.arn
  }
}

resource "aws_lb_listener" "forward_to_strategy_page_https" {
  count             = var.redirect_to_strategy_page && var.networking.enable_ssl_directory ? 1 : 0
  load_balancer_arn = aws_lb.fhir_api_alb.arn
  port              = 443
  protocol          = "HTTPS"
  certificate_arn   = data.aws_acm_certificate.directory_ssl_cert[0].arn

  default_action {
    type = "redirect"
    redirect {
      status_code = "HTTP_302"
      host        = "www.cms.gov"
      path        = "/priorities/health-technology-ecosystem/overview"
    }
  }
}

resource "aws_lb_listener_rule" "preview_flag_https" {
  count        = var.redirect_to_strategy_page ? 1 : 0
  listener_arn = aws_lb_listener.forward_to_strategy_page_https[0].arn

  condition {
    query_string {
      key   = "preview"
      value = "true"
    }
  }

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.fhir_api_tg.arn
  }
}

# api.directory.cms.gov and friends

resource "aws_alb" "fhir_api_alb_redirect" {
  name               = "${var.account_name}-fhir-redirect"
  internal           = var.private_load_balancer
  load_balancer_type = "application"
  security_groups    = [var.networking.alb_security_group_id]
  subnets            = var.networking.public_subnet_ids
}

resource "aws_alb_listener" "forward_to_directory_slash_fhir" {
  load_balancer_arn = aws_alb.fhir_api_alb_redirect.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      status_code = "HTTP_302"
      port        = 80
      host        = var.networking.directory_domain
      path        = "/fhir/#{path}"
    }
  }
}

data "aws_acm_certificate" "api_directory_ssl_cert" {
  count    = var.networking.enable_ssl_api ? 1 : 0
  domain   = var.networking.api_domain
  statuses = ["ISSUED"]
}

resource "aws_alb_listener" "forward_to_directory_slash_fhir_https" {
  count             = var.networking.enable_ssl_api ? 1 : 0
  load_balancer_arn = aws_alb.fhir_api_alb_redirect.arn
  port              = 443
  protocol          = "HTTPS"
  certificate_arn   = data.aws_acm_certificate.api_directory_ssl_cert[0].arn

  default_action {
    type = "redirect"
    redirect {
      status_code = "HTTP_302"
      port        = 443
      host        = var.networking.directory_domain
      path        = "/fhir/#{path}"
    }
  }
}
