resource "aws_eks_cluster" "apps_cluster" {
  name     = var.cluster_name
  role_arn = var.cluster_role_arn
  version  = var.cluster_version
  
  access_config {
    authentication_mode                         = "API_AND_CONFIG_MAP"
    bootstrap_cluster_creator_admin_permissions = true
  }
  
  bootstrap_self_managed_addons = false
  # REMOVED: deletion_protection = false (not supported in AWS provider 5.x)
  
  enabled_cluster_log_types = var.enabled_cluster_log_types
  
  kubernetes_network_config {
    ip_family         = "ipv4"
    service_ipv4_cidr = var.service_ipv4_cidr
  }
  
  upgrade_policy {
    support_type = "EXTENDED"
  }
  
  vpc_config {
    endpoint_private_access = var.vpc_config.endpoint_private_access
    endpoint_public_access  = var.vpc_config.endpoint_public_access
    public_access_cidrs     = var.vpc_config.public_access_cidrs
    subnet_ids              = var.subnet_ids
  }
  
  tags = merge(
    {
      Name        = var.cluster_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Region      = var.aws_region
    },
    var.tags
  )
  
  lifecycle {
    ignore_changes = [
      version
    ]
  }
}