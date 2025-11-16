include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "${get_parent_terragrunt_dir()}/../../../terraform-resources/iam"
}

inputs = {
  environment = "qa"
  aws_region  = "ap-south-1"
  
  eks_cluster_role_name    = "qa-ap-south-1-eks-cluster-role"
  eks_node_group_role_name = "qa-ap-south-1-eks-node-role"
  
  tags = {
    Environment = "qa"
    Region      = "ap-south-1"
    Project     = "GLAD"
    Team        = "DevOps"
    CostCenter  = "Engineering"
    ManagedBy   = "Terraform"
  }
}