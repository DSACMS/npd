terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket = "npd-terraform"
    key = "terraform.tfstate"
    region = "us-gov-west-1"
    use_lockfile = true
  }
}

provider "aws" {
  region = "us-gov-west-1"
}

data "aws_region" "current" {}
data "aws_partition" "current" {}
data "aws_caller_identity" "current" {}

locals {
  account_name = "dsac-gov-west-sandbox"

  iam_path             = "/delegatedadmin/developer/"
  permissions_boundary = "arn:${data.aws_partition.current.partition}:iam::${data.aws_caller_identity.current.account_id}:policy/cms-cloud-admin/developer-boundary-policy"
}

data "aws_vpc" "default" {
  filter {
    name   = "tag:Name"
    values = [local.account_name]
  }
}

data "aws_subnets" "private" {
  filter {
    name   = "tag:Name"
    values = ["${local.account_name}-private-a", "${local.account_name}-private-b"]
  }
}

data "aws_subnets" "public" {
  filter {
    name   = "tag:Name"
    values = ["${local.account_name}-public-a", "${local.account_name}-public-b"]
  }
}

resource "aws_default_security_group" "default" {
  vpc_id = data.aws_vpc.default.id
}

resource "aws_ecr_repository" "app" {
  name = var.name
}

module "ecs" {
  source  = "terraform-aws-modules/ecs/aws"
  version = "5.12.1"

  cluster_name = var.name

  fargate_capacity_providers = {
    FARGATE = {
      default_capacity_provider_strategy = {
        weight = 50
        base   = 20
      }
    }
    FARGATE_SPOT = {
      default_capacity_provider_strategy = {
        weight = 50
      }
    }
  }
}

resource "aws_iam_role" "ecs_task_execution" {
  name = "ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })

  path                 = local.iam_path
  permissions_boundary = local.permissions_boundary
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws-us-gov:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_policy" "ecs_task_logs_policy" {
  name        = "ecs-task-logs-policy"
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
        Resource = "arn:${data.aws_partition.current.partition}:logs:*:${data.aws_caller_identity.current.account_id}:log-group:/ecs/${var.name}*:*"
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_logs" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = aws_iam_policy.ecs_task_logs_policy.arn
}

resource "aws_cloudwatch_log_group" "logs" {
  name = "/ecs/${var.name}"
}

resource "aws_ecs_task_definition" "app" {
  family                   = "${var.name}-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([
    {
      name      = var.name
      image     = var.container_image
      essential = true
      #   command = ["start"]
      environment  = []
      portMappings = [{ containerPort = var.container_port, hostPort = var.container_port }]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${var.name}"
          "awslogs-region"        = data.aws_region.current.name
          "awslogs-stream-prefix" = var.name
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

resource "aws_ecs_service" "app" {
  name            = "${var.name}-service"
  cluster         = module.ecs.cluster_id
  task_definition = aws_ecs_task_definition.app.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    subnets          = data.aws_subnets.public.ids
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = var.name
    container_port   = var.container_port
  }
}

resource "aws_security_group" "ecs" {
  name   = "${var.name}-sg"
  vpc_id = data.aws_vpc.default.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = var.container_port
    to_port     = var.container_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_subnet_group" "db" {
  name       = "${var.name}-db-subnet"
  subnet_ids = data.aws_subnets.public.ids
}

resource "aws_security_group" "rds_sg" {
  name        = "${var.name}-rds-sg"
  description = "Allow ECS tasks to access RDS"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # We wouldn't do this in prod, but this is to make local connections easier
  }

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }

  ingress {
    from_port = 5432
    to_port = 5432
    protocol = "tcp"
    security_groups = [aws_security_group.glue_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_lb" "alb" {
  name               = "${var.name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.ecs.id]
  subnets            = data.aws_subnets.public.ids
}

resource "aws_lb_target_group" "app" {
  name        = "${var.name}-tg"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = data.aws_vpc.default.id
  target_type = "ip"

  health_check {
    path                = "/health"
    port                = var.container_port
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 10
    matcher             = "200"
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

module "rds" {
  source  = "terraform-aws-modules/rds/aws"
  version = "6.12.0"

  identifier             = "${var.name}-db"
  engine                 = "postgres"
  engine_version         = "17"
  family                 = "postgres17"
  instance_class         = var.db_instance_class
  allocated_storage      = 100
  db_name                = var.db_name
  username               = var.db_name
  publicly_accessible    = true
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.db.name
}

resource "aws_security_group" "glue_sg" {
  name = "glue-sg"
  description = "Common security group for Glue jobs"
  vpc_id = data.aws_vpc.default.id
}

resource "aws_vpc_security_group_ingress_rule" "glue_sg_allow_connections_from_self" {
  security_group_id = aws_security_group.glue_sg.id
  ip_protocol = "-1"
  referenced_security_group_id = aws_security_group.glue_sg.id
}

resource "aws_vpc_security_group_egress_rule" "glue_gs_allow_outbound_connections" {
  security_group_id = aws_security_group.glue_sg.id
  ip_protocol = "-1"
  cidr_ipv4 = "0.0.0.0/0"
}

resource "aws_s3_bucket" "glue_scripts" {
  bucket = "${var.name}-glue-scripts-bucket"
}

resource "aws_s3_object" "glue_job_script" {
  bucket = aws_s3_bucket.glue_scripts.bucket
  key    = "scripts/loadFIPS.py"
  source = abspath("${path.module}/../etls/loadFIPS/loadFIPS.py") # local path
  etag   = filemd5(abspath("${path.module}/../etls/loadFIPS/loadFIPS.py"))
}

resource "aws_s3_object" "glue_job_script_requirements" {
  bucket = aws_s3_bucket.glue_scripts.bucket
  key    = "scripts/requirements.txt"
  source = abspath("${path.module}/../etls/loadFIPS/requirements.txt") # local path
  etag   = filemd5(abspath("${path.module}/../etls/loadFIPS/requirements.txt"))
}

resource "aws_glue_job" "python_shell_job" {
  name         = "load-fips-python-shell-job"
  description  = "A python job that loads FIPS data"
  glue_version = "5.0"
  role_arn     = aws_iam_role.glue_job_role.arn
  max_capacity = "0.0625"
  max_retries  = 0
  timeout      = 2880
  connections  = []

  command {
    script_location = "s3://${aws_s3_object.glue_job_script.bucket}/${aws_s3_object.glue_job_script.key}"
    name            = "pythonshell"
    python_version  = "3.9"
  }

  default_arguments = {
    "--job-language"                     = "python" # Default is python
    # TODO: Glue 5.0 supports passing a requirements.txt instead of specific dependencies in the infrastructure definition
    # could not get it to work so I'm just passing these manually
    "--additional-python-modules"        = "requests==2.32.3, pandas==2.3.1, sqlalchemy==2.0.41, python-dotenv==1.1.1, psycopg2-binary==2.9.10"
    "--MAX_RETRIES"                      = "3"
    "--DB_SECRET_ARN"                    = module.rds.db_instance_master_user_secret_arn
    "--DB_HOST"                          = module.rds.db_instance_address
    "--DB_PORT"                          = module.rds.db_instance_port
    "--DB_NAME"                          = var.db_name
  }

  execution_property {
    max_concurrent_runs = 1
  }

  tags = {
    "ManagedBy" = "AWS"
  }
}

# IAM role for Glue jobs
resource "aws_iam_role" "glue_job_role" {
  name = "glue-job-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_policy" "glue_job_policy" {
  name = "glue-job-custom-policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "s3:GetObject"
        Effect = "Allow"
        Resource = [
          aws_s3_bucket.glue_scripts.arn,
          "${aws_s3_bucket.glue_scripts.arn}/*"
        ]
      },
      {
        Action = "secretsmanager:GetSecretValue",
        Effect = "Allow"
        Resource = [
          module.rds.db_instance_master_user_secret_arn
        ]
      }
    ]
  })
}

resource "aws_iam_policy_attachment" "glue_job_policy_attachment" {
  name = "glue_job_policy_attachment"
  policy_arn = aws_iam_policy.glue_job_policy.arn
  roles = [aws_iam_role.glue_job_role.name]
}

resource "aws_iam_policy_attachment" "glue_job_managed_policy_attachment" {
  name = "glue_job_managed_policy_attachment"
  policy_arn = "arn:aws-us-gov:iam::aws:policy/service-role/AWSGlueServiceRole"
  roles = [aws_iam_role.glue_job_role.name]
}
