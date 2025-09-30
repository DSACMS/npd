## Subnet configuration
data "aws_subnets" "database_subnets" {
  filter {
    name = "tag:Name"
    values = [
      "${var.account_name}-private-a",
      "${var.account_name}-private-b",
    ]
  }
}

resource "aws_db_subnet_group" "database_subnets" {
  name       = "${var.account_name}-database-subnets"
  subnet_ids = data.aws_subnets.database_subnets.ids
}

data "aws_subnets" "etl_subnets" {
  filter {
    name = "tag:Name"
    values = [
      "${var.account_name}-private-c"
    ]
  }
}

data "aws_subnets" "public_subnets" {
  filter {
    name = "tag:Name"
    values = [
      "${var.account_name}-public-a",
      "${var.account_name}-public-b",
      "${var.account_name}-public-c"
    ]
  }
}

## Security groups
data "aws_ec2_managed_prefix_list" "cmsvpn" {
  filter {
    name   = "prefix-list-name"
    values = ["cmscloud-v4-shared-services-prod-1"]
  }
}

resource "aws_security_group" "fhir_api_alb" {
  description = "Defines traffic flows to the FHIR API application load balancer"
  name        = "${var.account_name}-fhir-api-load-balancer-sq"
  vpc_id      = var.vpc_id
}

resource "aws_vpc_security_group_ingress_rule" "cmsvpn_to_fhir_api_alb_http" {
  description = "Allows connections to the FHIR API from the VPN over HTTP"
  security_group_id = aws_security_group.fhir_api_db_sg.id
  ip_protocol = "tcp"
  from_port = 80
  to_port = 80
  prefix_list_id = data.aws_ec2_managed_prefix_list.cmsvpn.id
}

resource "aws_vpc_security_group_ingress_rule" "cmsvpn_to_fhir_api_alb_https" {
  description = "Allows connections to the FHIR API from the VPN over HTTPS"
  security_group_id = aws_security_group.fhir_api_db_sg.id
  ip_protocol = "tcp"
  from_port = 443
  to_port = 443
  prefix_list_id = data.aws_ec2_managed_prefix_list.cmsvpn.id
}

resource "aws_security_group" "fhir_api_sg" {
  description = "Defines traffic flows to the FHIR REST API"
  name        = "${var.account_name}-fhir-api-sg"
  vpc_id      = var.vpc_id
}

resource "aws_security_group" "fhir_api_db_sg" {
  description = "Defines traffic flows to the FHIR DB"
  name        = "${var.account_name}-fhir-api-db-sg"
  vpc_id      = var.vpc_id
}

resource "aws_vpc_security_group_ingress_rule" "cmsvpn_to_fhir_api_db" {
  description = "Allows connections to the FHIR API database from the VPN"
  security_group_id = aws_security_group.fhir_api_db_sg.id
  ip_protocol = "tcp"
  from_port = 5432
  to_port = 5432
  prefix_list_id = data.aws_ec2_managed_prefix_list.cmsvpn.id
}

resource "aws_security_group" "fhir_etl_db_sg" {
  description = "Defines traffic flows to the FHIR ETL DB"
  name        = "${var.account_name}-fhir-etl-db-sg"
  vpc_id      = var.vpc_id
}

resource "aws_vpc_security_group_ingress_rule" "cmsvpn_to_etl_db" {
  description = "Allows connections to the ETL database from the VPN"
  security_group_id = aws_security_group.fhir_etl_db_sg.id
  ip_protocol = "tcp"
  from_port = 5432
  to_port = 5432
  prefix_list_id = data.aws_ec2_managed_prefix_list.cmsvpn.id
}

resource "aws_security_group" "fhir_etl_sg" {
  description = "Defines traffic flows to and from the ETL processes"
  name        = "${var.account_name}-fhir-etl-sg"
  vpc_id      = var.vpc_id
}