resource "aws_eks_addon" "cluster_addons" {
  for_each = var.cluster_addons
  
  cluster_name                = aws_eks_cluster.apps_cluster.name
  addon_name                  = each.value.addon_name
  addon_version               = try(each.value.addon_version, null)
  resolve_conflicts_on_create = try(each.value.resolve_conflicts_on_create, "OVERWRITE")
  resolve_conflicts_on_update = try(each.value.resolve_conflicts_on_update, "OVERWRITE")
  preserve                    = try(each.value.preserve, true)
  service_account_role_arn    = try(each.value.service_account_role_arn, null)
  configuration_values        = try(each.value.configuration_values, null)
  
  tags = merge(
    {
      Name        = each.value.addon_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Region      = var.aws_region
    },
    var.tags
  )
  
  depends_on = [
    aws_eks_cluster.apps_cluster,
    aws_eks_node_group.apps_cluster_ng
  ]
  
  lifecycle {
    ignore_changes = [
      modified_at
    ]
  }
}