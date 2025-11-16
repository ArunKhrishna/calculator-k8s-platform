include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../../../../terraform-resources/vpc-networking/route_table"
}

dependency "vpc" {
  config_path = "../vpc"
  
  mock_outputs = {
    vpc_id = "vpc-mock-12345"
  }
  mock_outputs_allowed_terraform_commands = ["validate", "plan"]
}

dependency "igw" {
  config_path = "../igw"
  
  mock_outputs = {
    igw_id = "igw-mock-12345"
  }
  mock_outputs_allowed_terraform_commands = ["validate", "plan"]
}

dependency "nat" {
  config_path = "../nat"
  
  mock_outputs = {
    nat_gateway_id = "nat-mock-12345"
  }
  mock_outputs_allowed_terraform_commands = ["validate", "plan"]
}

dependency "subnet" {
  config_path = "../subnet"
  
  mock_outputs = {
    public_subnet_ids  = ["subnet-mock-1", "subnet-mock-2"]
    private_subnet_ids = ["subnet-mock-3", "subnet-mock-4"]
  }
  mock_outputs_allowed_terraform_commands = ["validate", "plan"]
}

inputs = {
  environment = "qa"
  aws_region  = "ap-south-1"
  
  vpc_id = dependency.vpc.outputs.vpc_id
  
  route_tables = {
    public = {
      name = "qa-public"
      routes = [
        {
          cidr_block = "0.0.0.0/0"
          gateway_id = dependency.igw.outputs.igw_id
        }
      ]
      subnet_associations = dependency.subnet.outputs.public_subnet_ids
      is_main             = false
      tags                = {}
    }
    
    private = {
      name = "qa-private"
      routes = [
        {
          cidr_block     = "0.0.0.0/0"
          nat_gateway_id = dependency.nat.outputs.nat_gateway_id
        }
      ]
      subnet_associations = dependency.subnet.outputs.private_subnet_ids
      is_main             = false
      tags                = {}
    }
    
    main = {
      name                = "qa-main"
      routes              = []
      subnet_associations = []
      is_main             = true
      tags                = {}
    }
  }
}