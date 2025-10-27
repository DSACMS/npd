resource "aws_route53_zone" "internal_npd_zone" {
  name = "${var.account_name}.internal.cms.gov"

  vpc {
    vpc_id = var.vpc_id
  }
}

resource "aws_route53_record" "dagster_record" {
  zone_id = aws_route53_zone.internal_npd_zone.zone_id
  name = "etl"
  type = "CNAME"
  ttl = "300"
  records = [var.dagster_ui_alb_dns_name]
}
