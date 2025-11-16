include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../../../../terraform-resources/vpc-networking/subnet"
}

dependency "vpc" {
  config_path = "../vpc"
  
  mock_outputs = {
    vpc_id = "vpc-mock-12345"
  }
  mock_outputs_allowed_terraform_commands = ["validate", "plan"]
}

locals {
  cluster_name = ["qa-eks"]
  public_subnet_tags = merge(
    {
      "kubernetes.io/role/elb" = 1
    },
    { for cluster in local.cluster_name :
      "kubernetes.io/cluster/${cluster}" => "shared"
    }
  )  
  private_subnet_tags = merge(
    {
      "kubernetes.io/role/internal-elb" = 1
    },
    { for cluster in local.cluster_name :
      "kubernetes.io/cluster/${cluster}" => "shared"
    }
  )
}

inputs = {
  environment = "qa"
  aws_region  = "ap-south-1"
  
  vpc_id = dependency.vpc.outputs.vpc_id
  private_subnet_tags = local.private_subnet_tags
  public_subnet_tags = local.public_subnet_tags
  
  subnets = {
    "qa-private-ap-south-1a" = {
      cidr_block              = "10.0.0.0/19"
      availability_zone       = "ap-south-1a"
      map_public_ip_on_launch = false
      subnet_type             = "private"
    }
    
    "qa-private-ap-south-1b" = {
      cidr_block              = "10.0.32.0/19"
      availability_zone       = "ap-south-1b"
      map_public_ip_on_launch = false
      subnet_type             = "private"
    }
    
    "qa-public-ap-south-1a" = {
      cidr_block              = "10.0.64.0/19"
      availability_zone       = "ap-south-1a"
      map_public_ip_on_launch = false
      subnet_type             = "public"
    }
    
    "qa-public-ap-south-1b" = {
      cidr_block              = "10.0.96.0/19"
      availability_zone       = "ap-south-1b"
      map_public_ip_on_launch = false
      subnet_type             = "public"
    }
  }
}