resource "aws_subnet" "ac9_subnet" {
  #for_each solves resource level duplication issue when multiple subnets are needed
  for_each = var.subnets

  vpc_id                  = var.vpc_id
  cidr_block              = each.value.cidr_block
  availability_zone       = each.value.availability_zone
  map_public_ip_on_launch = each.value.map_public_ip_on_launch

  #merge solves tag duplication issue and allows common and specific tags in the ternary operator

  tags = merge(
    {
      Name        = each.key
      Environment = var.environment
      ManagedBy   = "Terraform"
      Region      = var.aws_region
      SubnetType  = each.value.subnet_type
    },
    var.common_tags,
    each.value.subnet_type == "private" ? var.private_subnet_tags : var.public_subnet_tags
  )

  lifecycle {
    prevent_destroy = true
  }
}
