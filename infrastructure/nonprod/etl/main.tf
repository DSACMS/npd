data "aws_region" "current" {}
data "aws_partition" "current" {}
data "aws_caller_identity" "current" {}

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
      Principal = { Service = "ecs-tasks.amazon.com" }
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
        Action = "sts:AssumeRole"
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

# resource "aws_iam_role" "dagster_task_role" {
#   name = "${var.account_name}-etl-service-task-role"
#   description = "Describes actions the ETL tasks can make"
#   poli
# }

resource "aws_ecs_task_definition" "dagster_daemon" {
  family                   = "dagster-daemon"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  task_role_arn            = local.task_role_arn
  execution_role_arn       = local.execution_role_arn

  container_definitions = jsonencode([
    {
      name      = "dagster-daemon"
      image     = var.dagster_image
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = local.log_group
          "awslogs-region"        = var.region
          "awslogs-stream-prefix" = "dagster-daemon"
        }
      }
      command = ["dagster-daemon", "run", "-w", "${var.dagster_home}/workspace.yaml"]
      environment = concat(
        [
          { name = "DAGSTER_HOME", value = var.dagster_home },
          { name = "DAGSTER_POSTGRES_HOST", value = var.postgres_host },
          { name = "DAGSTER_POSTGRES_PASSWORD", value = var.postgres_password }
        ],
        var.environment
      )
      secrets = var.secrets
    }
  ])
}

resource "aws_ecs_service" "dagster_daemon" {
  name            = "dagster-daemon"
  cluster         = var.ecs_cluster_id
  desired_count   = 1
  launch_type     = "FARGATE"
  task_definition = aws_ecs_task_definition.dagster_daemon.arn

  network_configuration {
    subnets         = var.daemon_subnet_ids
    security_groups = [aws_security_group.dagster.id]
    # when running in public subnet, consider setting assign_public_ip = true
    # however, this is not recommended for production as it exposes the container to the internet
    assign_public_ip = var.create_lb ? true : var.assign_public_ip
  }

  force_new_deployment = true
}


resource "aws_ecs_task_definition" "dagster_webserver" {
  family                   = "dagster-webserver"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  task_role_arn            = local.task_role_arn
  execution_role_arn       = local.execution_role_arn

  container_definitions = jsonencode([
    {
      name      = "dagster-webserver"
      image     = var.dagster_image
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = local.log_group
          "awslogs-region"        = var.region
          "awslogs-stream-prefix" = "dagster-webserver"
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
      command = ["dagster-webserver", "--host", "0.0.0.0", "--port", "80", "-w", "${var.dagster_home}/workspace.yaml"]
      environment = concat(
        [
          { name = "DAGSTER_HOME", value = var.dagster_home },
          { name = "DAGSTER_POSTGRES_HOST", value = var.postgres_host },
          { name = "DAGSTER_POSTGRES_PASSWORD", value = var.postgres_password }
        ],
        var.environment
      )
      secrets = var.secrets
    }
  ])
}


resource "aws_ecs_service" "dagster-webserver" {
  name            = "dagster-webserver"
  cluster         = var.ecs_cluster_id
  desired_count   = 1
  launch_type     = "FARGATE"
  task_definition = aws_ecs_task_definition.dagster_webserver.arn

  network_configuration {
    subnets         = var.webserver_subnet_ids
    security_groups = [aws_security_group.dagster.id]
    # when running in public subnet, consider setting assign_public_ip = true
    # however, this is not recommended for production as it exposes the container to the internet
    assign_public_ip = var.create_lb ? true : var.assign_public_ip
  }

  dynamic "load_balancer" {
    for_each = var.create_lb ? [1] : []
    content {
      target_group_arn = local.lb_target_group_arn
      container_name   = "dagster-webserver"
      container_port   = 80
    }
  }

  force_new_deployment = true
}