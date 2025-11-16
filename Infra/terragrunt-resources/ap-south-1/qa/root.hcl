locals {
  # Get relative path from root.hcl to current directory
  path_parts  = compact(split("/", path_relative_to_include()))
  
  # For path like ["iam"], we're at qa/iam, so we need to go up to find region
  # The directory structure is: ap-south-1/qa/{service}
  # So we need to look at parent directories
  aws_region  = "ap-south-1"  # Hardcode for now since all configs are in ap-south-1
  environment = length(local.path_parts) > 0 ? local.path_parts[0] : "qa"
  service     = basename(get_terragrunt_dir())
}

remote_state {
  backend = "s3"
  config = {
    bucket         = "terraform-state-files-india"
    key            = "${local.aws_region}/${local.environment}/${local.service}/terraform.tfstate"
    region         = "ap-south-1"
    encrypt        = true
    #dynamodb_table = "ac9-terraform-state-locks"
  }
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
}

generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
provider "aws" {
  region = "${local.aws_region}"
  
  default_tags {
    tags = {
      Environment = "${local.environment}"
      Region      = "${local.aws_region}"
      Service     = "${local.service}"
      ManagedBy   = "Terraform"
    }
  }
}

terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
EOF
}