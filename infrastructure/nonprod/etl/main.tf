resource "aws_s3_bucket" "etl_bronze" {
  bucket = "${var.account_name}-etl-bronze"
}
