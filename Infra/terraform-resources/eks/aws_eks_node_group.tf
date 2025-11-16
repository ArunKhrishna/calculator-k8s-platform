resource "aws_eks_node_group" "apps_cluster_ng" {
  for_each = var.node_groups

  cluster_name    = aws_eks_cluster.apps_cluster.name
  node_group_name = each.value.name
  node_role_arn   = var.node_role_arn
  subnet_ids      = var.subnet_ids
  
  ami_type       = each.value.ami_type
  capacity_type  = each.value.capacity_type
  disk_size      = each.value.disk_size
  instance_types = each.value.instance_types
  version        = var.cluster_version
  release_version = var.node_group_release_version

  scaling_config {
    desired_size = each.value.desired_size
    max_size     = each.value.max_size
    min_size     = each.value.min_size
  }

  update_config {
    max_unavailable = 1
  }

  dynamic "node_repair_config" {
    for_each = each.value.enable_node_repair ? [] : [1]
    content {
      enabled = false
    }
  }

  dynamic "taint" {
    for_each = each.value.taints
    content {
      key    = taint.value.key
      value  = taint.value.value
      effect = taint.value.effect
    }
  }

  labels = each.value.labels

  tags = merge(
    {
      Name        = each.value.name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Region      = var.aws_region
    },
    var.tags
  )

  depends_on = [
    aws_eks_cluster.apps_cluster
  ]

  lifecycle {
    create_before_destroy = true
    ignore_changes        = [scaling_config[0].desired_size]
  }
}
