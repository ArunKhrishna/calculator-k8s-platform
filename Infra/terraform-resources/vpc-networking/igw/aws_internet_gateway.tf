resource "aws_internet_gateway" "ac9_internet_gateway" {
  vpc_id = var.vpc_id

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
