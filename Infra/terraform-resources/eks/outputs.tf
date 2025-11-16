# Cluster Outputs
output "cluster_id" {
  description = "The name of the EKS cluster"
  value       = aws_eks_cluster.apps_cluster.id
}

output "cluster_arn" {
  description = "The ARN of the EKS cluster"
  value       = aws_eks_cluster.apps_cluster.arn
}

output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = aws_eks_cluster.apps_cluster.endpoint
  sensitive   = true
}

output "cluster_security_group_id" {
  description = "Security group ID attached to the EKS cluster"
  value       = aws_eks_cluster.apps_cluster.vpc_config[0].cluster_security_group_id
}

output "cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = aws_eks_cluster.apps_cluster.certificate_authority[0].data
  sensitive   = true
}

output "cluster_version" {
  description = "The Kubernetes server version for the cluster"
  value       = aws_eks_cluster.apps_cluster.version
}

output "cluster_platform_version" {
  description = "The platform version for the cluster"
  value       = aws_eks_cluster.apps_cluster.platform_version
}

output "cluster_status" {
  description = "Status of the EKS cluster"
  value       = aws_eks_cluster.apps_cluster.status
}

output "cluster_oidc_issuer_url" {
  description = "The URL on the EKS cluster OIDC Issuer"
  value       = aws_eks_cluster.apps_cluster.identity[0].oidc[0].issuer
}

# Node Group Outputs - FIXED REFERENCE
output "node_groups" {
  description = "Map of node group details"
  value = {
    for k, ng in aws_eks_node_group.apps_cluster_ng : k => {
      id                   = ng.id
      arn                  = ng.arn
      status               = ng.status
      capacity_type        = ng.capacity_type
      instance_types       = ng.instance_types
      node_group_name      = ng.node_group_name
      resources            = ng.resources
      autoscaling_groups   = ng.resources[0].autoscaling_groups
    }
  }
}

output "node_group_ids" {
  description = "List of node group IDs"
  value       = [for ng in aws_eks_node_group.apps_cluster_ng : ng.id]
}

output "node_group_arns" {
  description = "List of node group ARNs"
  value       = [for ng in aws_eks_node_group.apps_cluster_ng : ng.arn]
}

output "node_group_statuses" {
  description = "Map of node group statuses"
  value       = { for k, ng in aws_eks_node_group.apps_cluster_ng : k => ng.status }
}