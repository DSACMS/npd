variable "name" { default = "ndh-pg-app" }
variable "db_name" { default = "ndh" }
variable "container_port" { default = 3000 }
variable "container_image" { default = "public.ecr.aws/aws-containers/ecsdemo-frontend:latest" }
variable "ecs_cpu" { default = 512 }
variable "ecs_memory" { default = 1024 }
variable "db_instance_class" { default = "db.t3.micro" }
