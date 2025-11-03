module "database_migration_service" {
  source  = "terraform-aws-modules/dms/aws"
  version = "~> 2.0"

  # Subnet group
  repl_subnet_group_name        = module.networking.private_subnet_group_name # check is this correct?
  repl_subnet_group_description = "The name of the subnet group used with the databases"
  repl_subnet_group_subnet_ids  = module.networking.private_subnet_ids

  endpoints = {
    source = {
      database_name               = "npd_etl"
      endpoint_id                 = "npd-east-dev-etl-db"
      endpoint_type               = "source"
      engine_name                 = "postgresql"
      username                    = "npd_etl"
      password                    = "youShouldPickABetterPassword123!" # where to get this?
      port                        = 5432
      server_name                 = "npd-east-dev-etl-db.cc3asw0omsvl.us-east-1.rds.amazonaws.com" # can this be a reference instead of hard coded?
      ssl_mode                    = "require"
    }

    destination = {
      database_name = "npd"
      endpoint_id   = "npd-east-dev-fhir-api-db"
      endpoint_type = "target"
      engine_name   = "postgresql"
      username      = "npd"
      password      = "passwordsDoNotNeedToMatch789?" # where to get this?
      port          = 5432
      server_name   = "npd-east-dev-fhir-api-db.cc3asw0omsvl.us-east-1.rds.amazonaws.com" # can this be a reference instead of hard coded?
      ssl_mode      = "require"
    }
  }

  replication_tasks = {
    test-dms-task = {
      replication_task_id       = "test-dms-task"
      migration_type            = "cdc"
      replication_task_settings = file("configs/task_settings.json")
      table_mappings            = file("configs/table_mappings.json")
      source_endpoint_key       = "npd-east-dev-etl-db"
      target_endpoint_key       = "npd-east-dev-fhir-api-db"

      serverless_config = {
        max_capacity_units     = 8
        min_capacity_units     = 4
        multi_az               = false # should be true for prod?
        vpc_security_group_ids = [module.networking.etl_db_security_group_id] # or [module.networking.db_security_group_id] ?
      }
    }
  }

  tags = {
    Terraform   = "true"
    Environment = "dev" # what's the variable for the env?
  }
}