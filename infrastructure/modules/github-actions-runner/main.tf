data "aws_caller_identity" "current" {}

locals {
  account_id = data.aws_caller_identity.current.account_id
}

resource "aws_iam_role" "github_runner_resource_creation_role" {
  description = "Role to be assumed for resource creation"
  name        = "${var.account_name}-github-actions-runner-creation-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
        }
        StringLike = {
          "token.actions.githubusercontent.com:sub" = "repo:CMS-Enterprise/NPD:*"
        }
      }
      Principal = {
        Federated = "arn:aws:iam::${local.account_id}:oidc-provider/token.actions.githubusercontent.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "github_runner_has_admin" {
  role       = aws_iam_role.github_runner_resource_creation_role.id
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

resource "aws_iam_role_policy_attachment" "github_runner_has_ado_restriction" {
  role       = aws_iam_role.github_runner_resource_creation_role.id
  policy_arn = "arn:aws:iam::${local.account_id}:policy/ADO-Restriction-Policy"
}

resource "aws_iam_role_policy_attachment" "github_runner_has_region_restriction" {
  role       = aws_iam_role.github_runner_resource_creation_role.id
  policy_arn = "arn:aws:iam::${local.account_id}:policy/CMSCloudApprovedRegions"
}

resource "aws_iam_role_policy_attachment" "github_runner_has_user_creation_restriction" {
  role       = aws_iam_role.github_runner_resource_creation_role.id
  policy_arn = "arn:aws:iam::${local.account_id}:policy/ct-iamCreateUserRestrictionPolicy"
}

resource "aws_instance" "github_actions_instance" {
  ami           = "ami-04345af6ff8317b5e"
  instance_type = "m5.xlarge"
  vpc_security_group_ids = var.security_group_ids
  subnet_id            = var.subnet_id
  iam_instance_profile = "cms-cloud-base-ec2-profile-v4"
  tags = {
    Name = "github-actions-runner-instance"
  }
}
