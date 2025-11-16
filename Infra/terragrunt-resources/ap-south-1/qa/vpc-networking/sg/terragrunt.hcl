include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../../../../terraform-resources/vpc-networking/sg"
}

dependency "vpc" {
  config_path = "../vpc"
  
  mock_outputs = {
    vpc_id = "vpc-mock-12345"
  }
  mock_outputs_allowed_terraform_commands = ["validate", "plan"]
}

inputs = {
  environment = "qa"
  aws_region  = "ap-south-1"
  
  vpc_id = dependency.vpc.outputs.vpc_id
  
  security_groups = {
    qa_glad_rds = {
      name        = "qa-glad-rds-sg"
      description = "Security group for GLAD RDS Aurora PostgreSQL"
      
      ingress_rules = [
        {
          description = "PostgreSQL access from VPC"
          from_port   = 5432
          to_port     = 5432
          protocol    = "tcp"
          cidr_blocks = ["10.0.0.0/16"]
          self        = false
        }
      ]
      
      egress_rules = [
        {
          description = "Allow all outbound"
          from_port   = 0
          to_port     = 0
          protocol    = "-1"
          cidr_blocks = ["0.0.0.0/0"]
          self        = false
        }
      ]
      
      tags = {
        Purpose = "RDS-Database"
        Project = "GLAD"
      }
    }
    
    qa_default = {
      name        = "qa-default-sg"
      description = "Default VPC security group"
      
      ingress_rules = [
        {
          description = "Allow all from self"
          from_port   = 0
          to_port     = 0
          protocol    = "-1"
          self        = true
        }
      ]
      
      egress_rules = [
        {
          description = "Allow all outbound"
          from_port   = 0
          to_port     = 0
          protocol    = "-1"
          cidr_blocks = ["0.0.0.0/0"]
          self        = false
        }
      ]
      
      tags = {}
    }
  }
  
  common_tags = {
    Environment = "qa"
    ManagedBy   = "Terragrunt"
    Region      = "ap-south-1"
  }
}