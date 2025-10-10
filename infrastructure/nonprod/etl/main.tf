resource "aws_s3_bucket" "frontend_bucket" {
  bucket = "${var.account_name}-etl-bronze"
}
