/*
This is exploratory AWS Glue infrastructure work that we can use if we commit to using AWS Glue. Unreferenced from
main.tf for the time being.
 */

resource "aws_security_group" "glue_sg" {
  name        = "glue-sg"
  description = "Common security group for Glue jobs"
  vpc_id      = data.aws_vpc.default.id
}

resource "aws_vpc_security_group_ingress_rule" "glue_sg_allow_connections_from_self" {
  security_group_id            = aws_security_group.glue_sg.id
  ip_protocol                  = "-1"
  referenced_security_group_id = aws_security_group.glue_sg.id
}

resource "aws_vpc_security_group_egress_rule" "glue_gs_allow_outbound_connections" {
  security_group_id = aws_security_group.glue_sg.id
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_s3_bucket" "glue_scripts" {
  bucket        = "${var.name}-glue-scripts-bucket"
  force_destroy = true
}

resource "aws_s3_bucket" "aws_glue_input_bucket" {
  bucket        = "${var.name}-glue-s3-input"
  force_destroy = true
}

resource "aws_s3_bucket" "aws_glue_output_bucket" {
  bucket        = "${var.name}-glue-s3-output"
  force_destroy = true
}

resource "aws_glue_catalog_database" "aws_glue_catalog" {
  name = "${var.name}-glue-data-catalog"
}

resource "aws_glue_crawler" "aws_glue_crawler" {
  database_name = aws_glue_catalog_database.aws_glue_catalog.name
  name          = "${var.name}-glue-data-catalog-crawler"
  role          = aws_iam_role.glue_job_role.arn
  schedule      = "cron(0 12 * * ? *)"

  s3_target {
    path = "s3://${aws_s3_bucket.aws_glue_input_bucket.bucket}"
  }
}

resource "aws_s3_object" "glue_job_script" {
  bucket = aws_s3_bucket.glue_scripts.bucket
  key    = "scripts/loadFIPS.py"
  source = abspath("${path.module}/../etls/loadFIPS/loadFIPS.py") # local path
  etag   = filemd5(abspath("${path.module}/../etls/loadFIPS/loadFIPS.py"))
}

resource "aws_s3_object" "glue_job_script_pyspark" {
  bucket = aws_s3_bucket.glue_scripts.bucket
  key    = "scripts/nppesToS3.py"
  source = abspath("${path.module}/../etls/nppesToS3/nppesToS3.py") # local path
  etag   = filemd5(abspath("${path.module}/../etls/nppesToS3/nppesToS3.py"))
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
    "--job-language"              = "python" # Default is python
    "--additional-python-modules" = replace(file(abspath("${path.module}/../etls/loadFIPS/requirements.txt")), "\n", ", ")
    "--MAX_RETRIES"               = "3"
    "--DB_SECRET_ARN"             = module.rds.db_instance_master_user_secret_arn
    "--DB_HOST"                   = module.rds.db_instance_address
    "--DB_PORT"                   = module.rds.db_instance_port
    "--DB_NAME"                   = var.db_name
  }

  execution_property {
    max_concurrent_runs = 1
  }

  tags = {
    "ManagedBy" = "AWS"
  }
}

resource "aws_glue_job" "pyspark_job" {
  name              = "nppes-to-s3-pyspark-job"
  description       = "A simple pyspark job that moves a single table from one location to another"
  glue_version      = "5.0"
  role_arn          = aws_iam_role.glue_job_role.arn
  number_of_workers = 2
  worker_type       = "G.1X"
  max_retries       = 0
  timeout           = 2880
  connections       = []

  command {
    script_location = "s3://${aws_s3_object.glue_job_script.bucket}/${aws_s3_object.glue_job_script_pyspark.key}"
    name            = "glueetl"
    python_version  = "3"
  }

  default_arguments = {
    "--job-bookmark-option" = "job-bookmark-enable"
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
          "${aws_s3_bucket.glue_scripts.arn}/*",
          aws_s3_bucket.aws_glue_input_bucket.arn,
          "${aws_s3_bucket.aws_glue_input_bucket.arn}/*",
        ]
      },
      {
        Action = "s3:PutObject"
        Effect = "Allow"
        Resource = [
          aws_s3_bucket.aws_glue_output_bucket.arn,
          "${aws_s3_bucket.aws_glue_output_bucket.arn}/*",
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
  name       = "glue_job_policy_attachment"
  policy_arn = aws_iam_policy.glue_job_policy.arn
  roles      = [aws_iam_role.glue_job_role.name]
}

resource "aws_iam_policy_attachment" "glue_job_managed_policy_attachment" {
  name       = "glue_job_managed_policy_attachment"
  policy_arn = "arn:aws-us-gov:iam::aws:policy/service-role/AWSGlueServiceRole"
  roles      = [aws_iam_role.glue_job_role.name]
}