include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../../../../terraform-resources/vpc-networking/nat"
}

dependency "subnet" {
  config_path = "../subnet"
  
  mock_outputs = {
    public_subnet_ids = ["subnet-mock-12345"]
  }
  mock_outputs_allowed_terraform_commands = ["validate", "plan"]
}

dependency "eip" {
  config_path = "../elastic-ips"
  
  mock_outputs = {
    eip_allocation_ids = {
      qa_nat = "eipalloc-mock-12345"
    }
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

inputs = {
  environment = "qa"
  aws_region  = "ap-south-1"
  
  subnet_id = dependency.subnet.outputs.public_subnet_ids[0]
  allocation_id = dependency.eip.outputs.eip_allocation_ids["qa_nat"]
  
  name              = "qa-nat"
  connectivity_type = "public"
  
  tags = {}
}