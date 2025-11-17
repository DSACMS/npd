resource "aws_route53_zone" "internal_dns" {
  name = var.directory_domain
}

resource "aws_route53_record" "ns" {
  zone_id = aws_route53_zone.internal_dns.zone_id
  name    = var.directory_domain
  type    = "NS"
  ttl     = "30"
  records = aws_route53_zone.internal_dns.name_servers
}

resource "aws_route53_record" "directory" {
  count   = var.enable_internal_domain_for_directory ? 1 : 0
  zone_id = aws_route53_zone.internal_dns.zone_id
  name    = var.directory_domain
  type    = "CNAME"
  ttl     = "300"
  records = [var.directory_alb_dns_name]
}

resource "aws_route53_record" "api" {
  count   = var.enable_internal_domain_for_directory ? 1 : 0
  zone_id = aws_route53_zone.internal_dns.zone_id
  name    = var.api_domain
  type    = "CNAME"
  ttl     = "300"
  records = [var.api_alb_dns_name]
}

resource "aws_route53_record" "etl" {
  zone_id = aws_route53_zone.internal_dns.zone_id
  name    = var.etl_domain
  type    = "CNAME"
  ttl     = "300"
  records = [var.etl_alb_dns_name]
}
