# terragrunt.hcl - Updated configuration with prefix delegation
include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "../../../../terraform-resources/eks"
}

dependency "iam" {
  config_path = "../iam"
  
  mock_outputs = {
    eks_cluster_role_arn = "arn:aws:iam::123456789012:role/mock-cluster-role"
    eks_node_group_role_arn = "arn:aws:iam::123456789012:role/mock-node-role"
  }
  mock_outputs_allowed_terraform_commands = ["validate", "plan"]
}

dependency "subnet" {
  config_path = "../vpc-networking/subnet"
  
  mock_outputs = {
    private_subnet_ids = ["subnet-1234", "subnet-5678"]
  }
  mock_outputs_allowed_terraform_commands = ["validate", "plan"]
}

inputs = {
  environment = "qa"
  aws_region  = "ap-south-1"
  
  cluster_name     = "qa-eks"
  cluster_version  = "1.31"
  cluster_role_arn = dependency.iam.outputs.eks_cluster_role_arn
  subnet_ids       = dependency.subnet.outputs.private_subnet_ids
  
  vpc_config = {
    endpoint_private_access = true
    endpoint_public_access  = true
    public_access_cidrs     = ["0.0.0.0/0"]
  }
  
  enabled_cluster_log_types = ["api", "audit", "authenticator"]
  service_ipv4_cidr        = "172.20.0.0/16"
  
  node_role_arn              = dependency.iam.outputs.eks_node_group_role_arn
  node_group_release_version = "1.31.13-20251103"
  
  node_groups = {
    # Keep existing micro node group
    micro = {
      name           = "qa-eks-ng-micro-final"
      ami_type       = "AL2023_x86_64_STANDARD"
      instance_types = ["t2.micro"]
      desired_size   = 2
      max_size       = 2
      min_size       = 2
      capacity_type  = "ON_DEMAND"
      disk_size      = 20
      labels = {
        "node-type" = "micro"
        "workload"  = "system"
      }
      taints = []
      enable_node_repair = true
    }
    
    # New medium node group with prefix delegation
    medium = {
      name           = "qa-eks-ng-medium-v2"
      ami_type       = "AL2023_x86_64_STANDARD"
      instance_types = ["t3.medium"]
      desired_size   = 2
      max_size       = 4
      min_size       = 2
      capacity_type  = "ON_DEMAND"
      disk_size      = 30
      labels = {
        "node-type" = "medium"
        "workload"  = "general"
        "env"       = "qa"
      }
      taints = []
      enable_node_repair = true
    }
  }
  
  cluster_addons = {
    vpc_cni = {
      addon_name    = "vpc-cni"
      addon_version = "v1.18.5-eksbuild.1"
      resolve_conflicts_on_create = "OVERWRITE"
      resolve_conflicts_on_update = "OVERWRITE"
      preserve = false  # Changed from true to allow updates
      configuration_values = jsonencode({
        env = {
          ENABLE_PREFIX_DELEGATION = "true"
          WARM_PREFIX_TARGET = "1"
          ENABLE_POD_ENI = "true"
        }
      })
    }
    eks_pod_identity_agent = {
      addon_name    = "eks-pod-identity-agent"
      addon_version = "v1.3.2-eksbuild.2"
      resolve_conflicts_on_create = "OVERWRITE"
      resolve_conflicts_on_update = "PRESERVE"
      preserve = true
    }
    # Optional: Add CoreDNS and kube-proxy
    coredns = {
      addon_name    = "coredns"
      addon_version = "v1.11.3-eksbuild.2"
      resolve_conflicts_on_create = "OVERWRITE"
      resolve_conflicts_on_update = "PRESERVE"
      preserve = true
    }
    kube_proxy = {
      addon_name    = "kube-proxy"
      addon_version = "v1.31.0-eksbuild.5"
      resolve_conflicts_on_create = "OVERWRITE"
      resolve_conflicts_on_update = "PRESERVE"
      preserve = true
    }
  }
  
  tags = {
    Project    = "GLAD"
    Team       = "DevOps"
    CostCenter = "Engineering"
    NodeGroup  = "medium-prefix-delegation"
  }
}