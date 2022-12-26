terraform {
  required_version = "~> 1.2.5"

  required_providers {
    aws = "~> 4.46.0"
  }

  backend "s3" {
    bucket = "terraform-state-334fa816"
    key    = "url-service/project.tfstate"
    region = "us-east-1"
  }
}

locals {
  project_name       = "url-service"
  global_prefix_name = "${local.project_name}-${terraform.workspace}"

  env_variables = yamldecode(file("../../server/settings.yml"))["${terraform.workspace}"]

  tags = {
    project              = local.project_name
    type                 = "personal-project"
    managed_by_terraform = "true"
  }
}

provider "aws" {
  region = var.aws_region
}
