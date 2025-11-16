include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../../../../terraform-resources/vpc-networking/elastic-ips"
}

inputs = {
  environment = "qa"
  aws_region  = "ap-south-1"
  
  elastic_ips = {
    qa_nat = {
      name                 = "qa-nat"
      domain               = "vpc"
      network_interface_id = null
      instance_id          = null
      associate_with_nat   = false
      
      tags = {}
    }
  }
}