terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
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

data "aws_caller_identity" "current" {}

data "aws_vpc" "default" {
  filter {
    name   = "tag:Name"
    values = [local.account_name]
  }
}

module "domains" {
  source = "../../modules/domains"

  tier = var.tier
}

module "dns" {
  source = "../../modules/dns"

  enable_internal_domain_for_directory = true
  namespace_domain                     = module.domains.namespace_domain
  api_domain                           = module.domains.api_domain
  api_alb_dns_name                     = module.fhir-api.api_alb_dns_name
  directory_domain                     = module.domains.directory_domain
  directory_alb_dns_name               = module.fhir-api.api_dot_alb_dns_name
  directory_alb_zone_id                = module.fhir-api.api_alb_zone_id
  etl_domain                           = module.domains.etl_domain
  etl_alb_dns_name                     = module.etl.etl_ui_alb_dns_name
}

module "repositories" {
  source = "../../modules/repositories"

  account_name = local.account_name
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
  instance_class          = "db.t3.large"
  allocated_storage       = 100
  max_allocated_storage   = 1000
  storage_type            = "gp3"
  publicly_accessible     = false
  username                = "npd"
  db_name                 = "npd"
  db_subnet_group_name    = module.networking.private_subnet_group_name
  vpc_security_group_ids  = [module.networking.db_security_group_id]
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
  instance_class          = "db.t3.large"
  allocated_storage       = 2000
  max_allocated_storage   = 4000
  publicly_accessible     = false
  username                = "npd_etl"
  db_name                 = "npd_etl"
  db_subnet_group_name    = module.networking.private_subnet_group_name
  vpc_security_group_ids  = [module.networking.etl_db_security_group_id]
  backup_retention_period = 7             # Remove automated snapshots after 7 days
  backup_window           = "03:00-04:00" # 11PM EST

  parameters = [
    # Parameters altered to enable DMS to perform database replication
    # Need to install the pglogical extension on the server after creation:
    # create extension pglogical;
    # select * FROM pg_catalog.pg_extension
    { name = "rds.logical_replication", value = "1", apply_method = "pending-reboot" },
    { name = "wal_sender_timeout", value = "0" },
    { name = "shared_preload_libraries", value = "pglogical", apply_method = "pending-reboot" }
  ]
}

# ECS Cluster
module "ecs" {
  source  = "terraform-aws-modules/ecs/aws"
  version = "6.6.2"

  cluster_name = "${local.account_name}-ecs-cluster"
  default_capacity_provider_strategy = {
    FARGATE = {
      weight = 50
      base   = 20
    }
    FARGATE_SPOT = {
      weight = 50
    }
  }
}

# FHIR API Module
module "fhir-api" {
  source = "../../modules/fhir-api"

  account_name             = local.account_name
  fhir_api_migration_image = var.migration_image
  fhir_api_image           = var.fhir_api_image
  ecs_cluster_id           = module.ecs.cluster_id
  desired_task_count       = 2
  require_authentication   = var.require_authentication
  db = {
    db_instance_master_user_secret_arn = module.api-db.db_instance_master_user_secret_arn
    db_instance_address                = module.api-db.db_instance_address
    db_instance_port                   = module.api-db.db_instance_port
    db_instance_name                   = "npd_halloween_sjp"
  }
  networking = {
    private_subnet_ids    = module.networking.private_subnet_ids
    public_subnet_ids     = module.networking.public_subnet_ids
    alb_security_group_id = module.networking.alb_security_group_id
    api_security_group_id = module.networking.api_security_group_id
    vpc_id                = module.networking.vpc_id
    directory_domain      = module.domains.directory_domain
    enable_ssl_directory  = false
    api_domain            = module.domains.api_domain
    enable_ssl_api        = false
  }
}

# ETL Module
module "etl" {
  source = "../../modules/etl"

  account_name             = local.account_name
  dagster_image            = var.dagster_image
  fhir_api_migration_image = var.migration_image
  ecs_cluster_id           = module.ecs.cluster_id
  npd_sync_task_arn        = "arn:aws:dms:us-east-1:${data.aws_caller_identity.current.account_id}:replication-config:57J6Z4LH2JAUNKC3LS7RUETZUE"
  db = {
    db_instance_master_user_secret_arn = module.etl-db.db_instance_master_user_secret_arn
    db_instance_address                = module.etl-db.db_instance_address
    db_instance_port                   = module.etl-db.db_instance_port
    db_instance_name                   = module.etl-db.db_instance_name
  }
  networking = {
    private_subnet_ids        = module.networking.private_subnet_ids
    public_subnet_ids         = module.networking.public_subnet_ids
    etl_alb_security_group_id = module.networking.etl_alb_security_group_id
    etl_security_group_id     = module.networking.etl_security_group_id
    vpc_id                    = module.networking.vpc_id
  }
}

# Migrations module
module "migrations" {
  source = "../../modules/migrations"

  multi_az     = false
  account_name = local.account_name
  region       = var.region
  tier         = var.tier
  fhir_db = {
    db_instance_master_user_secret_arn = module.api-db.db_instance_master_user_secret_arn
    db_instance_address                = module.api-db.db_instance_address
    db_instance_port                   = module.api-db.db_instance_port
    db_instance_name                   = module.api-db.db_instance_name
  }
  etl_db = {
    db_instance_master_user_secret_arn = module.etl-db.db_instance_master_user_secret_arn
    db_instance_address                = module.etl-db.db_instance_address
    db_instance_port                   = module.etl-db.db_instance_port
    db_instance_name                   = module.etl-db.db_instance_name
  }
  networking = {
    private_subnet_group_name = module.networking.private_subnet_group_name
    private_subnet_ids        = module.networking.private_subnet_ids
    api_db_security_group_id  = module.networking.db_security_group_id
    etl_db_security_group_id  = module.networking.etl_db_security_group_id
    public_subnet_ids         = module.networking.public_subnet_ids
    vpc_id                    = module.networking.vpc_id
  }
}

# Frontend Module
module "frontend" {
  source       = "../../modules/frontend"
  account_name = local.account_name
}

# CI/CD
module "github-actions" {
  source = "../../modules/github-actions-runner"

  account_name = local.account_name
  security_group_ids = concat(
    module.networking.cmscloud_security_group_ids,
    [module.networking.github_action_runner_security_group_id]
  )
  subnet_ids                  = module.networking.private_subnet_ids
  ecs_cluster_id              = module.ecs.cluster_id
  github_runner_image         = var.github_runner_image
  enable_containerized_runner = true
}
