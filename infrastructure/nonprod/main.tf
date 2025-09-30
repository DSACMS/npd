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
  source = "./networking"

  vpc_id       = data.aws_vpc.default.id
  account_name = local.account_name
}

## ECR Repositories
resource "aws_ecr_repository" "fhir_api" {
  name = "${local.account_name}-fhir-api"
}

resource "aws_ecr_repository" "fhir_api_migrations" {
  name = "${local.account_name}-fhir-api-migrations"
}

## Application Database
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
  vpc_security_group_ids  = [ module.networking.db_security_group_id ]
  db_subnet_group_name    = module.networking.db_subnet_group_name
  backup_retention_period = 7             # Remove automated snapshots after 7 days
  backup_window           = "03:00-04:00" # 11PM EST
}

## ETL Database
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
  vpc_security_group_ids  = [ module.networking.db_security_group_id ]
  db_subnet_group_name    = module.networking.db_subnet_group_name
  backup_retention_period = 7             # Remove automated snapshots after 7 days
  backup_window           = "03:00-04:00" # 11PM EST
}

