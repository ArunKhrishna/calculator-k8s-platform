resource "aws_vpc" "glad_vpc" {
  cidr_block                           = var.cidr_block
  instance_tenancy                     = var.instance_tenancy
  enable_dns_hostnames                 = var.enable_dns_hostnames
  enable_dns_support                   = var.enable_dns_support
  enable_network_address_usage_metrics = var.enable_network_address_usage_metrics

  tags = merge(
    {
      Name        = var.name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Region      = var.aws_region
    },
    var.common_tags,
    var.tags
  )

  lifecycle {
    prevent_destroy = true
  }
}











