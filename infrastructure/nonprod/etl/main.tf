data "aws_region" "current" {}
data "aws_partition" "current" {}
data "aws_caller_identity" "current" {}

locals {
  dagster_home = "dagster_home"
}

resource "aws_ecr_repository" "dagster" {
  name = "${var.account_name}-dagster"
}

resource "aws_s3_bucket" "etl_bronze" {
  bucket = "${var.account_name}-etl-bronze"
}

resource "aws_iam_role" "dagster_execution_role" {
  name        = "${var.account_name}-dagster-task-execution-role"
  description = "Defines what AWS Actions the ECS task environment is allowed to make when setting up the ETL orchestrator"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_policy" "dagster_can_access_etl_database_secret" {
  name        = "${var.account_name}-etl-service-can-access-etl-database-secret"
  description = "Allows Dagster to access the ETL database RDS secret"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "secretsmanager:GetSecretValue",
        Effect = "Allow"
        Resource = [
          var.db.db_instance_master_user_secret_arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "dagster_can_access_etl_database_secret_attachment" {
  role       = aws_iam_role.dagster_execution_role.name
  policy_arn = aws_iam_policy.dagster_can_access_etl_database_secret.arn
}

resource "aws_iam_policy" "dagster_can_emit_logs" {
  name        = "${var.account_name}-etl-service-can-log-to-cloudwatch"
  description = "Allow Dagster to write logs to Cloudwatch"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogsEvents"
        ]
        Effect   = "Allow"
        Resource = "arn:${data.aws_partition.current.partition}:logs:*:${data.aws_caller_identity.current.account_id}:log-group:/ecs/${var.account_name}*:*"
      }
    ]
  })
}

resource "aws_iam_role" "dagster_task_role" {
  name = "${var.account_name}-etl-service-task-role"
  description = "Describes actions the ETL tasks can make"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_ecs_task_definition" "dagster_daemon" {
  family                   = "dagster-daemon"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  task_role_arn            = aws_iam_role.dagster_task_role.arn
  execution_role_arn       = aws_iam_role.dagster_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "${var.account_name}-dagster-daemon"
      image     = var.dagster_image
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${var.account_name}-dagster-daemon-logs"
          "awslogs-region"        = data.aws_region.current.name
          "awslogs-stream-prefix" = "${var.account_name}-dagster-daemon-logs"
        }
      }
      command = ["dagster-daemon", "run", "-w", "${local.dagster_home}/workspace.yaml"]
      environment = [
        { name = "DAGSTER_HOME", value = local.dagster_home },
        { name = "DAGSTER_POSTGRES_HOST", value = var.db.db_instance_address },
        { name = "DAGSTER_POSTGRES_DB", value = var.dagster_db_name }
      ],
      secrets = [
        {
          name = "DAGSTER_POSTGRES_USER",
          valueFrom = "${var.db.db_instance_master_user_secret_arn}:user::"
        },
        {
          name      = "DAGSTER_POSTGRES_PASSWORD",
          valueFrom = "${var.db.db_instance_master_user_secret_arn}:password::"
        }
      ]
    }
  ])
}

resource "aws_ecs_service" "dagster_daemon" {
  name            = "${var.account_name}-dagster-daemon"
  cluster         = var.ecs_cluster_id
  desired_count   = 1
  launch_type     = "FARGATE"
  task_definition = aws_ecs_task_definition.dagster_daemon.arn

  network_configuration {
    subnets         = var.networking.etl_subnet_ids
    security_groups = [var.networking.etl_security_group_id]
  }

  force_new_deployment = true
}


resource "aws_ecs_task_definition" "dagster_ui" {
  family                   = "${var.account_name}-dagster-ui"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  task_role_arn            = aws_iam_role.dagster_task_role.arn
  execution_role_arn       = aws_iam_role.dagster_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "${var.account_name}-dagster-ui"
      image     = var.dagster_image
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${var.account_name}-dagster-ui-logs"
          "awslogs-region"        = data.aws_region.current.name
          "awslogs-stream-prefix" = "${var.account_name}-dagster-ui-logs"
        }
      }
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
          protocol      = "tcp"
          name          = "http"
        }
      ]
      command = ["dagster-ui", "--host", "0.0.0.0", "--port", "80", "-w", "${local.dagster_home}/workspace.yaml"]
      environment = [
        { name = "DAGSTER_HOME", value = local.dagster_home },
        { name = "DAGSTER_POSTGRES_HOST", value = var.db.db_instance_address },
        { name = "DAGSTER_POSTGRES_DB", value = var.dagster_db_name }
      ],
      secrets = [
        {
          name = "DAGSTER_POSTGRES_USER",
          valueFrom = "${var.db.db_instance_master_user_secret_arn}:user::"
        },
        {
          name      = "DAGSTER_POSTGRES_PASSWORD",
          valueFrom = "${var.db.db_instance_master_user_secret_arn}:password::"
        }
      ]
    }
  ])
}

resource "aws_ecs_service" "dagster-ui" {
  name            = "${var.account_name}-dagster-ui"
  cluster         = var.ecs_cluster_id
  desired_count   = 1
  launch_type     = "FARGATE"
  task_definition = aws_ecs_task_definition.dagster_ui.arn

  network_configuration {
    subnets         = var.networking.etl_subnet_ids
    security_groups = [var.networking.etl_security_group_id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.dagster_ui.arn
    container_name   = "${var.account_name}-dagster-ui"
    container_port   = 80
  }

  force_new_deployment = true
}

resource "aws_lb" "dagster_ui_alb" {
  name = "${var.account_name}-dagster-ui-alb"
  internal = false # TODO I don't know what this means
  load_balancer_type = "application"
  security_groups = [var.networking.etl_webserver_alb_security_group_id]
  subnets = var.networking.public_subnet_ids
}

resource "aws_lb_target_group" "dagster_ui" {
  name = "${var.account_name}-dagster-ui-tg"
  port = 3001
  protocol = "HTTP"
  vpc_id = var.networking.vpc_id
  target_type = "ip"

  # TODO health check
}

resource "aws_alb_listener" "http" {
  load_balancer_arn = aws_lb.dagster_ui_alb.arn
  port = 80
  protocol = "HTTP"

  default_action {
    type = "forward"
    target_group_arn = aws_lb_target_group.dagster_ui.arn
  }
}

