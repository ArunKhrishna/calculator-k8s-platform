resource "aws_security_group" "ac9_security_group" {
  for_each = var.security_groups

  name        = each.value.name
  description = each.value.description
  vpc_id      = var.vpc_id

  tags = merge(
    {
      Name        = each.value.name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Region      = var.aws_region
    },
    var.common_tags,
    each.value.tags
  )

  lifecycle {
    prevent_destroy       = true
    create_before_destroy = true
  }
}