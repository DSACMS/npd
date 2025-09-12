# Terraform ECS Postgres App

Terraform configuration for provisioning the NPD AWS infrastructure. This will be added to as we build out more of the infrastructure. To read more about Terraform for AWS and explore a "Getting Started Guide," go [here](https://developer.hashicorp.com/terraform/tutorials/aws-get-started).

## Dependencies

* [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
* [Terraform CLI](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)
* [CTKey CLI Tool](https://cloud.cms.gov/getting-started-access-key-cli-tool) (n.b. ensure you add CTKey to PATH)


## Setup

### Authentication
Follow these setup steps to set and/or refresh your stored AWS credentials for this project.
1. Update the variables in `ctkey.sh` to match your application and AWS account.
  * Ensure that the IAM role aligns with a role you have access to (may be ct-ado-dsac-developer-admin instead of ct-ado-dsac-application-admin, depending on how your AWS perms were provisioned)
2. Run `./ctkey.sh`
3. Set the AWS_PROFILE environment variable with the profile name you chose

### Provision Resources
1. Create a `terraform.tfvars` file to pass custom values for the variables contained in `variables.tf`
2. Run

```sh
terraform init
terraform apply
```

Provisions the following:

- ECS cluster, service, and task definitions
- ECR repository to publish custom container images to
- ALB to direct traffic to ECS on port 80
- RDS database with public connectivity to 5432 (**for local dev, be careful**). Note: Refer to AWS Secrets Manager to find the password of the provisioned database user.
3. Create a [cloud service request ticket](https://jiraent.cms.gov/plugins/servlet/desk/portal/22) to have the db instance added to the ZScaler Private Segment. Note: Unil this is completed, you will only be able to connect locally with ZScaler fully disabled (turning off Private Access is not sufficient).

### Modify Provisioned Resources
1. Change the settings in `main.tf`
2. Run

```sh
terraform apply
```

## Development

- Build a Docker container locally
- Push the Docker container to ECR, following the included instructions on the AWS console
- Update the container image variable by setting the `TF_VAR_container_image` environment variable as well as any other differences like `TF_VAR_container_port`
  - You can also specify these in a `.tfvars` file ignored by git
- Update any task definition parameters that are different for your container

## DSAC Sandbox

This infrastructure lives in the DSAC sandbox. A GitHub Actions workflow [deploy-to-sandbox.yml](../.github/workflows/deploy-to-sandbox.yml) updates the sandbox infrastructure when a PR to `main` is merged.

## Notes

- This is **not a production configuration**, in particular when it comes to security. It mostly focuses on handling a lot of the annoying footguns when getting started with a deployed dev environment
- This is a starting point that we will build off of
- This is very coupled to running in the DSAC sandbox environment
- In order to connect to the database, it is recommended that you set a connection timeout of 300 seconds.


## Notional Infrastructure Diagram
The below diagram is a rough hypothesis of the infrastructure components that will make up the National Provider Directory MVP.
![Notional architecture diagram](<Notional NPD System Diagram_2025-08-26_19-37-04.png>)