resource "aws_route53_zone" "internal_dns" {
  name = var.directory_domain
}

resource "aws_route53_record" "ns" {
  # creating a zone automatically creates an NS record
  # setting allow_overwrite to true updates the automatically
  # created record as a separate entity from the zone
  allow_overwrite = true
  zone_id = aws_route53_zone.internal_dns.zone_id
  name    = var.directory_domain
  type    = "NS"
  ttl     = 172800
  records = aws_route53_zone.internal_dns.name_servers
}

resource "aws_route53_record" "directory" {
  count   = var.enable_internal_domain_for_directory ? 1 : 0
  zone_id = aws_route53_zone.internal_dns.zone_id
  name    = var.directory_domain
  type    = "A"

  alias {
    name                   = var.directory_alb_dns_name
    zone_id                = var.directory_alb_zone_id
    evaluate_target_health = true
  }
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
