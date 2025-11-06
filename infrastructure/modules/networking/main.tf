## Subnet configuration
data "aws_subnets" "private_subnets" {
  filter {
    name = "tag:Name"
    values = [
      "${var.account_name}-private-a",
      "${var.account_name}-private-b",
      "${var.account_name}-private-c"
    ]
  }
}

## Preconfigured CMSCloud Security Groups
data "aws_security_groups" "cms_cloud_sg" {
  filter {
    name   = "group-name"
    values = ["cmscloud*"]
  }

  filter {
    name   = "vpc-id"
    values = [var.vpc_id]
  }
}



resource "aws_db_subnet_group" "private_subnets" {
  name       = "${var.account_name}-private-subnets"
  subnet_ids = data.aws_subnets.private_subnets.ids
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

### FHIR API Load Balancer

resource "aws_security_group" "fhir_api_alb_sg" {
  description = "Defines traffic flows to/from the FHIR API application load balancer"
  name        = "${var.account_name}-fhir-api-load-balancer-sg"
  vpc_id      = var.vpc_id
}

resource "aws_vpc_security_group_ingress_rule" "http_to_fhir_api_alb" {
  description       = "Accepts HTTP connections"
  security_group_id = aws_security_group.fhir_api_alb_sg.id
  ip_protocol = "TCP"
  from_port = 80
  to_port = 80
  cidr_ipv4 = "0.0.0.0/*"
}

resource "aws_vpc_security_group_ingress_rule" "https_to_fhir_api_alb" {
  description       = "Accepts HTTPS connections"
  security_group_id = aws_security_group.fhir_api_alb_sg.id
  ip_protocol = "TCP"
  from_port = 443
  to_port = 443
  cidr_ipv4 = "0.0.0.0/*"
}

resource "aws_vpc_security_group_egress_rule" "fhir_api_alb_can_make_outbound_requests" {
  description       = "Allow the FHIR API ALB to make outbound requests"
  security_group_id = aws_security_group.fhir_api_alb_sg.id
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}

### FHIR API

resource "aws_security_group" "fhir_api_sg" {
  description = "Defines traffic flows to/from the FHIR REST API"
  name        = "${var.account_name}-fhir-api-sg"
  vpc_id      = var.vpc_id
}

resource "aws_vpc_security_group_ingress_rule" "fhir_api_alb_can_access_fhir_api_sg" {
  description                  = "Accepts traffic from the FHIR API ALB"
  security_group_id            = aws_security_group.fhir_api_sg.id
  ip_protocol                  = "TCP"
  referenced_security_group_id = aws_security_group.fhir_api_alb_sg.id
  from_port                    = 80
  to_port                      = 80
}

resource "aws_vpc_security_group_ingress_rule" "fhir_api_alb_can_access_fhir_api_sg_healthcheck" {
  description                  = "Accepts traffic from the FHIR API ALB healthcheck"
  security_group_id            = aws_security_group.fhir_api_sg.id
  ip_protocol                  = "TCP"
  referenced_security_group_id = aws_security_group.fhir_api_alb_sg.id
  from_port                    = 8000
  to_port                      = 8000
}

resource "aws_vpc_security_group_egress_rule" "fhir_api_can_make_outbound_requests" {
  description       = "Allows the FHIR API to make outbound requests"
  security_group_id = aws_security_group.fhir_api_sg.id
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}

### FHIR API Database

resource "aws_security_group" "fhir_api_db_sg" {
  description = "Defines traffic flows to/from the FHIR DB"
  name        = "${var.account_name}-fhir-api-db-sg"
  vpc_id      = var.vpc_id
}

resource "aws_vpc_security_group_ingress_rule" "cmsvpn_to_fhir_api_db" {
  description       = "Accepts Postgres connections from the CMS VPN"
  security_group_id = aws_security_group.fhir_api_db_sg.id
  ip_protocol       = "tcp"
  from_port         = 5432
  to_port           = 5432
  prefix_list_id    = data.aws_ec2_managed_prefix_list.cmsvpn.id
}

resource "aws_vpc_security_group_ingress_rule" "fhir_api_can_access_fhir_api_db" {
  description                  = "Accepts Postgres connections from the FHIR API"
  security_group_id            = aws_security_group.fhir_api_db_sg.id
  ip_protocol                  = "tcp"
  from_port                    = 5432
  to_port                      = 5432
  referenced_security_group_id = aws_security_group.fhir_api_sg.id
}

resource "aws_vpc_security_group_ingress_rule" "etl_sg_can_connect_to_fhir_api_db" {
  description                  = "Accepts Postgres connections from ETL security group"
  security_group_id            = aws_security_group.fhir_api_db_sg.id
  ip_protocol                  = "tcp"
  from_port                    = 5432
  to_port                      = 5432
  referenced_security_group_id = aws_security_group.fhir_etl_db_sg.id
}

resource "aws_vpc_security_group_ingress_rule" "github_runner_can_connect_to_api_db" {
  description = "Allows the CI runner to access the API database"
  security_group_id = aws_security_group.fhir_api_db_sg.id
  ip_protocol = "TCP"
  from_port = 5432
  to_port = 5432
  referenced_security_group_id = aws_security_group.github_runner_security_group.id
}

### ETL Database

resource "aws_security_group" "fhir_etl_db_sg" {
  description = "Defines traffic flows to/from the FHIR ETL DB"
  name        = "${var.account_name}-fhir-etl-db-sg"
  vpc_id      = var.vpc_id
}

resource "aws_vpc_security_group_ingress_rule" "cmsvpn_to_etl_db" {
  description       = "Accepts Postgres connections from the CMS VPN"
  security_group_id = aws_security_group.fhir_etl_db_sg.id
  ip_protocol       = "tcp"
  from_port         = 5432
  to_port           = 5432
  prefix_list_id    = data.aws_ec2_managed_prefix_list.cmsvpn.id
}

resource "aws_vpc_security_group_ingress_rule" "etl_sg_can_connect_to_etl_db" {
  description                  = "Accepts Postgres connections from Dagster"
  security_group_id            = aws_security_group.fhir_etl_db_sg.id
  ip_protocol                  = "tcp"
  from_port                    = 5432
  to_port                      = 5432
  referenced_security_group_id = aws_security_group.etl_sg.id
}

resource "aws_vpc_security_group_ingress_rule" "github_runner_can_connect_to_etl_db" {
  description = "Allows the CI runner to access the ETL database"
  security_group_id = aws_security_group.fhir_etl_db_sg.id
  ip_protocol = "TCP"
  from_port = 5432
  to_port = 5432
  referenced_security_group_id = aws_security_group.github_runner_security_group.id
}

### ETL ALB Security Group

resource "aws_security_group" "etl_webserver_alb_sg" {
  description = "Defines traffic flows to and from the dagster application load balancer"
  name        = "${var.account_name}-dagster-etl-alb-sg"
  vpc_id      = var.vpc_id
}

resource "aws_vpc_security_group_ingress_rule" "http_to_etl_webserver_alb" {
  description       = "Accepts HTTP connections"
  security_group_id = aws_security_group.etl_webserver_alb_sg.id
  ip_protocol = "TCP"
  from_port = 80
  to_port = 80
  cidr_ipv4 = "0.0.0.0/*"
}

resource "aws_vpc_security_group_ingress_rule" "https_to_etl_webserver_alb" {
  description       = "Accepts HTTPS connections"
  security_group_id = aws_security_group.etl_webserver_alb_sg.id
  ip_protocol = "TCP"
  from_port = 443
  to_port = 443
  cidr_ipv4 = "0.0.0.0/*"
}

resource "aws_vpc_security_group_egress_rule" "etl_webserver_alb_can_make_outbound_connections" {
  description       = "Allows the Dagster UI application load balancer to make outbound connections"
  security_group_id = aws_security_group.etl_webserver_alb_sg.id
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}

### ETL security group

resource "aws_security_group" "etl_sg" {
  description = "Defines traffic flows to/from the ETL processes"
  name        = "${var.account_name}-etl-sg"
  vpc_id      = var.vpc_id
}

resource "aws_vpc_security_group_ingress_rule" "etl_processes_can_reach_themselves" {
  description                  = "Allows workers within the ETL security group to talk to each other"
  security_group_id            = aws_security_group.etl_sg.id
  ip_protocol                  = "-1"
  referenced_security_group_id = aws_security_group.etl_sg.id
}

resource "aws_vpc_security_group_ingress_rule" "dagster_ui_alb_can_access_dagster_ui" {
  description                  = "Accepts traffic from the Dagster ALB"
  security_group_id            = aws_security_group.etl_sg.id
  ip_protocol                  = "-1"
  referenced_security_group_id = aws_security_group.etl_webserver_alb_sg.id
}

resource "aws_vpc_security_group_egress_rule" "dagster_can_make_outgoing_requests" {
  description       = "Allows Dagster processes to make outgoing requests"
  security_group_id = aws_security_group.etl_sg.id
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}

### CI Runner Group

resource "aws_security_group" "github_runner_security_group" {
  description = "Defines traffic flows to/from the GitHub Action runner"
  name        = "${var.account_name}-github-actions-runner-sg"
  vpc_id      = var.vpc_id
}

resource "aws_vpc_security_group_egress_rule" "github_runner_can_make_outgoing_requests" {
  description       = "Allows the GitHub Runner instance to make outgoing requests"
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
  security_group_id = aws_security_group.github_runner_security_group.id
}
