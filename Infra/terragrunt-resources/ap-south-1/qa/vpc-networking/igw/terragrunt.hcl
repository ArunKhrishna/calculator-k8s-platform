include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../../../../terraform-resources/vpc-networking/igw"
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
  name = "ap-south-1-qa-igw"
  
  tags = {}
}