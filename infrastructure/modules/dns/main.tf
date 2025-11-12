# Production Zone

locals {
  dev = {
    etl       = "etl.dev.directory.internal.cms.gov"
    api       = "api.dev.directory.internal.cms.gov"
    directory = "dev.directory.internal.cms.gov"
  }
  impl = {
    etl       = "etl.impl.directory.internal.cms.gov"
    api       = "api.impl.directory.internal.cms.gov"
    directory = "impl.directory.internal.cms.gov"
  }
  prod = {
    etl       = "etl.directory.internal.cms.gov"
    api       = "api.directory.cms.gov" # public route
    directory = "directory.cms.gov" # public route
  }
}

resource "aws_route53_zone" "internal_dns" {
  name = "directory.internal.cms.gov"
}

resource "aws_route53_record" "prod_ns" {
  zone_id = aws_route53_zone.internal_dns.zone_id
  name    = "directory.internal.cms.gov"
  type    = "NS"
  ttl     = "30"
  records = aws_route53_zone.dev.name_servers
}

# Note: API and APP are public facing in prod
# so they won't be specified as an internal route

resource "aws_route53_record" "prod_dagster_ui" {
  zone_id = aws_route53_zone.internal_dns.zone_id
  name    = local.prod.directory
  type    = "CNAME"
  ttl     = "300"
  records = [var.prod_dagster_ui_dns_name]
}

# Impl Zone

# IMPL doesn't exist yet, uncomment after it is created

# resource "aws_route53_zone" "impl" {
#   name = local.impl.directory
# }
#
# resource "aws_route53_record" "impl_ns" {
#   zone_id = aws_route53_zone.internal_dns.zone_id
#   name    = local.impl.directory
#   type    = "NS"
#   ttl     = "30"
#   records = aws_route53_zone.dev.name_servers
# }
#
# resource "aws_route53_record" "impl_directory" {
#   zone_id = aws_route53_zone.internal_dns.zone_id
#   name    = local.impl.directory
#   type    = "CNAME"
#   ttl     = "300"
#   records = [var.impl_directory_dns_name]
# }
#
# resource "aws_route53_record" "impl_dagster_ui" {
#   zone_id = aws_route53_zone.internal_dns.zone_id
#   name    = local.impl.etl
#   type    = "CNAME"
#   ttl     = "300"
#   records = [var.impl_etl_ui_dns_name]
# }
#
# resource "aws_route53_record" "impl_api" {
#   zone_id = aws_route53_zone.internal_dns.zone_id
#   name    = local.impl.api
#   type    = "CNAME"
#   ttl     = "300"
#   records = [var.impl_api_dns_name]
# }

# Dev Zone

resource "aws_route53_zone" "dev" {
  name = local.dev.directory
}

resource "aws_route53_record" "dev_ns" {
  zone_id = aws_route53_zone.internal_dns.zone_id
  name    = local.dev.directory
  type    = "NS"
  ttl     = "30"
  records = aws_route53_zone.dev.name_servers
}

resource "aws_route53_record" "dev_directory" {
  zone_id = aws_route53_zone.internal_dns.zone_id
  name    = local.dev.directory
  type    = "CNAME"
  ttl     = "300"
  records = [var.dev_directory_dns_name]
}

resource "aws_route53_record" "dev_dagster_ui" {
  zone_id = aws_route53_zone.internal_dns.zone_id
  name    = local.dev.etl
  type    = "CNAME"
  ttl     = "300"
  records = [var.dev_etl_ui_dns_name]
}

resource "aws_route53_record" "dev_api" {
  zone_id = aws_route53_zone.internal_dns.zone_id
  name    = local.dev.api
  type    = "CNAME"
  ttl     = "300"
  records = [var.dev_api_dns_name]
}

