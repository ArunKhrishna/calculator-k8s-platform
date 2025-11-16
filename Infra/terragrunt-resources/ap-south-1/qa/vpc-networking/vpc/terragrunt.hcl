include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../../../../terraform-resources/vpc-networking/vpc"
}

inputs = {
  environment = "qa"
  aws_region  = "ap-south-1"
  
  cidr_block                           = "10.0.0.0/16"
  name                                 = "ap-south-1-qa-vpc"
  enable_dns_hostnames                 = true
  enable_dns_support                   = true
  instance_tenancy                     = "default"
  enable_network_address_usage_metrics = false
  
  tags = {}
}