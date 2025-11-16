  resource "aws_nat_gateway" "ac9_nat_gateway" {
    allocation_id     = var.allocation_id
    subnet_id         = var.subnet_id
    connectivity_type = var.connectivity_type

    tags = merge(
      {
        Name        = var.name
        Environment = var.environment
        ManagedBy   = "Terraform"
        Region      = var.aws_region
      },
      var.tags
    )

    lifecycle {
      prevent_destroy = true
    }

    # NAT Gateway depends on Internet Gateway being available
    # This is implicit through subnet's route table
  }
