terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket       = "npd-east-nonprod-terraform"
    key          = "terraform.dev.tfstate"
    region       = "us-east-1"
    use_lockfile = true
  }
}

provider "aws" {
  region = var.region
}

locals {
  account_name = "npd-east-${var.tier}"
}

data "aws_vpc" "default" {
  filter {
    name   = "tag:Name"
    values = [local.account_name]
  }
}

module "networking" {
  source = "../../modules/networking"

  vpc_id       = data.aws_vpc.default.id
  account_name = local.account_name
}

# Application Database
module "api-db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "6.12.0"

  identifier              = "${local.account_name}-fhir-api-db"
  engine                  = "postgres"
  engine_version          = "17"
  family                  = "postgres17"
  instance_class          = "db.t3.micro"
  allocated_storage       = 20
  publicly_accessible     = false
  username                = "npd"
  vpc_security_group_ids  = [module.networking.db_security_group_id]
  db_subnet_group_name    = module.networking.db_subnet_group_name
  backup_retention_period = 7             # Remove automated snapshots after 7 days
  backup_window           = "03:00-04:00" # 11PM EST
}

# ETL Database
module "etl-db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "6.12.0"

  identifier              = "${local.account_name}-etl-db"
  engine                  = "postgres"
  engine_version          = "17"
  family                  = "postgres17"
  instance_class          = "db.t3.micro"
  allocated_storage       = 100
  publicly_accessible     = false
  username                = "npd_etl"
  vpc_security_group_ids  = [module.networking.db_security_group_id]
  db_subnet_group_name    = module.networking.db_subnet_group_name
  backup_retention_period = 7             # Remove automated snapshots after 7 days
  backup_window           = "03:00-04:00" # 11PM EST
}

# ECS Cluster
module "ecs" {
  source  = "terraform-aws-modules/ecs/aws"
  version = "5.12.1"

  cluster_name = "${local.account_name}-ecs-cluster"

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

# FHIR API Module
module "fhir-api" {
  source = "../../modules/fhir-api"

  account_name             = local.account_name
  app_db_name              = "npd"
  fhir_api_migration_image = var.migration_image
  fhir_api_image           = var.fhir_api_image
  ecs_cluster_id           = module.ecs.cluster_id
  db = {
    db_instance_master_user_secret_arn = module.api-db.db_instance_master_user_secret_arn
    db_instance_address                = module.api-db.db_instance_address
    db_instance_port                   = module.api-db.db_instance_port
  }
  networking = {
    db_subnet_ids         = module.networking.db_subnet_ids
    public_subnet_ids     = module.networking.public_subnet_ids
    alb_security_group_id = module.networking.alb_security_group_id
    api_security_group_id = module.networking.api_security_group_id
    vpc_id                = module.networking.vpc_id
  }
}

# ETL Module
module "etl" {
  source = "../../modules/etl"

  account_name = local.account_name
}

# Frontend Module
module "frontend" {
  source       = "../../modules/frontend"
  account_name = local.account_name
}

