  data "aws_secretsmanager_secret_version" "etl_db" {
      secret_id = var.etl_db.db_instance_master_user_secret_arn
  }
  data "aws_secretsmanager_secret_version" "fhir_db" {
      secret_id = var.fhir_db.db_instance_master_user_secret_arn
  }

  locals {
    etl_db_password  = jsondecode(data.aws_secretsmanager_secret_version.etl_db.secret_string).password
    fhir_db_password = jsondecode(data.aws_secretsmanager_secret_version.fhir_db.secret_string).password
    account_name     = "${var.region}-${var.tier}"
    multi_az         = var.multi_az
    table_mappings   = jsonencode({
      "rules": [
          {
              "rule-id": 1,
              "rule-name": "etl-selection-rule",
              "rule-type": "selection",
              "rule-action": "include",
              "object-locator": {
                  "schema-name": "npd",
                  "table-name": "%"
              },
              "filters": []
          },
          {
              "rule-id": 2,
              "rule-name": "etl-transformation-rule",
              "rule-type": "transformation",
              "rule-target": "table",
              "rule-action": "rename",
              "object-locator": {
                  "schema-name": "npd",
                  "table-name": "%"
              },
            "value": "npd-${var.region}-${var.tier}-${module.database_migration_service.endpoints["fhir-api-destination"].database_name}-migrated"
          }
      ]
    })
  }

  module "networking" {
  source = "../../modules/networking"

  vpc_id       = var.networking.vpc_id
  account_name = local.account_name
}

module "database_migration_service" {
  source  = "terraform-aws-modules/dms/aws"
  version = "~> 2.6.0"

  # Subnet group
  repl_subnet_group_name        = module.networking.private_subnet_group_name
  repl_subnet_group_description = "The DMS ETL replication subnet group"
  repl_subnet_group_subnet_ids  = module.networking.private_subnet_ids

  endpoints = {
    etl-source = {
      database_name = var.etl_db.db_instance_name
      endpoint_id   = "npd-east-${var.tier}-etl-source"
      endpoint_type = "source"
      engine_name   = "postgresql"
      username      = var.etl_db.db_instance_name
      password      = local.etl_db_password
      port          = 5432
      server_name   = var.etl_db.db_instance_address
      ssl_mode      = "require"
    }

    fhir-api-destination = {
      database_name = var.fhir_db.db_instance_name
      endpoint_id   = "npd-${var.region}-${var.tier}-fhir-api-destination"
      endpoint_type = "target"
      engine_name   = "postgresql"
      username      = var.fhir_db.db_instance_name
      password      = local.fhir_db_password
      port          = 5432
      server_name   = var.fhir_db.db_instance_address
      ssl_mode      = "require"
    }
  }

  replication_tasks = {
    etl_replication_task = {
      replication_task_id       = "npd-${var.region}-${var.tier}-etl-replication-task"
      migration_type            = "cdc"
      replication_task_settings = file("${path.module}/configs/task_settings.json")
      table_mappings            = local.table_mappings
      source_endpoint_arn       = module.database_migration_service.endpoints["etl-source"].endpoint_arn
      source_endpoint_key       = "etl-source"
      target_endpoint_arn       = module.database_migration_service.endpoints["fhir-api-destination"].endpoint_arn
      target_endpoint_key       = "fhir-api-destination"

      serverless_config = {
        max_capacity_units     = 8
        min_capacity_units     = 4
        multi_az               = var.multi_az
        vpc_security_group_ids = [module.networking.etl_db_security_group_id, module.networking.db_security_group_id]
      }
    }
  }

  tags = {
    Terraform   = "true"
    Environment = var.tier
  }
}