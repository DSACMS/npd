resource "aws_s3_bucket" "etl_bronze" {
  bucket = "${var.account_name}-etl-bronze"
}

data "aws_region" "current" {}
data "aws_partition" "current" {}
data "aws_caller_identity" "current" {}

# Log Groups

resource "aws_cloudwatch_log_group" "dagster_ui_log_group" {
  name              = "/ecs/${var.account_name}-dagster-ui-logs"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "dagster_daemon_log_group" {
  name              = "/ecs/${var.account_name}-dagster-daemon-logs"
  retention_in_days = 30
}

# ECS Roles and Policies

resource "aws_iam_role" "dagster_execution_role" {
  name        = "${var.account_name}-dagster-execution-role"
  description = "Defines what AWS actions the Dagster task execution environment is allowed to make"
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
  role       = aws_iam_role.dagster_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_policy" "dagster_can_access_etl_db_secret" {
  name        = "${var.account_name}-dagster-can-access-etl-database-secret"
  description = "Allows ECS to access the RDS secret"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "secretsmanager:GetSecretValue",
        Effect = "Allow"
        Resource = [
          var.db.db_instance_master_user_secret_arn,
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "dagster_can_access_database_secret_attachment" {
  role       = aws_iam_role.dagster_execution_role.name
  policy_arn = aws_iam_policy.dagster_can_access_etl_db_secret.arn
}

resource "aws_iam_policy" "dagster_logs_policy" {
  name        = "${var.account_name}-dagster-can-log-to-cloudwatch"
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

resource "aws_iam_role_policy_attachment" "dagster_can_create_cloudwatch_logs" {
  policy_arn = aws_iam_policy.dagster_logs_policy.id
  role       = aws_iam_role.dagster_execution_role.id
}

resource "aws_iam_role" "dagster_task_role" {
  name        = "${var.account_name}-etl-service-task-role"
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

resource "aws_iam_policy" "dagster_can_read_bronze_bucket" {
  name        = "${var.account_name}-dagster-can-read-bronze-bucket"
  description = "Allow ECS tasks to read and write to bronze bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:*"
        ]
        Effect = "Allow"
        Resource = [
          aws_s3_bucket.etl_bronze.arn,
          "${aws_s3_bucket.etl_bronze.arn}/*"
        ]
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "dagster_can_read_bronze_bucket_attachment" {
  policy_arn = aws_iam_policy.dagster_can_read_bronze_bucket.arn
  role       = aws_iam_role.dagster_task_role.id
}

resource "aws_ecs_task_definition" "dagster_daemon" {
  family                   = "${var.account_name}-dagster-daemon"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "2048"
  memory                   = "8192"
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
          "awslogs-group"         = "/ecs/${var.account_name}"
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = var.account_name
        }
      }
      command = ["dagster-daemon", "run"]
      environment = [
        { name = "DAGSTER_POSTGRES_HOST", value = var.db.db_instance_address },
        { name = "DAGSTER_POSTGRES_DB", value = var.db.db_instance_name },
        { name = "S3_REGION", value = "us-east-1" }
      ],
      secrets = [
        {
          name      = "DAGSTER_POSTGRES_USER",
          valueFrom = "${var.db.db_instance_master_user_secret_arn}:username::"
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
  name                   = "${var.account_name}-dagster-daemon"
  cluster                = var.ecs_cluster_id
  desired_count          = 1
  launch_type            = "FARGATE"
  task_definition        = aws_ecs_task_definition.dagster_daemon.arn
  enable_execute_command = true

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
  cpu                      = "2048"
  memory                   = "8192"
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
          "awslogs-group"         = "/ecs/${var.account_name}"
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = var.account_name
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
      command = ["dagster-webserver", "--host", "0.0.0.0", "--port", "80"]
      environment = [
        { name = "DAGSTER_POSTGRES_HOST", value = var.db.db_instance_address },
        { name = "DAGSTER_POSTGRES_DB", value = var.db.db_instance_name },
        { name = "S3_DATA_BUCKET", value = aws_s3_bucket.etl_bronze.bucket },
        { name = "S3_REGION", value = "us-east-1" }
      ],
      secrets = [
        {
          name      = "DAGSTER_POSTGRES_USER",
          valueFrom = "${var.db.db_instance_master_user_secret_arn}:username::"
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
  name                   = "${var.account_name}-dagster-ui"
  cluster                = var.ecs_cluster_id
  desired_count          = 1
  launch_type            = "FARGATE"
  task_definition        = aws_ecs_task_definition.dagster_ui.arn
  enable_execute_command = true

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
  name               = "${var.account_name}-dagster-ui-alb"
  internal           = false # TODO I don't know what this means
  load_balancer_type = "application"
  security_groups    = [var.networking.etl_alb_security_group_id]
  subnets            = var.networking.public_subnet_ids
}

resource "aws_lb_target_group" "dagster_ui" {
  name        = "${var.account_name}-dagster-ui-tg"
  port        = 3001
  protocol    = "HTTP"
  vpc_id      = var.networking.vpc_id
  target_type = "ip"

  health_check {
    path                = "/"
    port                = 80
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 10
    matcher             = "200"
  }
}

resource "aws_alb_listener" "http" {
  load_balancer_arn = aws_lb.dagster_ui_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.dagster_ui.arn
  }
}