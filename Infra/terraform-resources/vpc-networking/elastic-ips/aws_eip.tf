resource "aws_eip" "ac9_eips" {
  for_each = var.elastic_ips

  domain               = each.value.domain
  # network_interface    = each.value.network_interface_id

  tags = merge(
    {
      Name        = each.value.name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Region      = var.aws_region
    }
  )

  lifecycle {
    prevent_destroy = false
  }
}