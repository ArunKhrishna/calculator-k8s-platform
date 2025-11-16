resource "aws_route_table" "ac9_route_table" {
  for_each = var.route_tables

  vpc_id = var.vpc_id

  dynamic "route" {
    for_each = each.value.routes
    content {
      cidr_block                 = lookup(route.value, "cidr_block", null)
      ipv6_cidr_block            = lookup(route.value, "ipv6_cidr_block", null)
      destination_prefix_list_id = lookup(route.value, "destination_prefix_list_id", null)
      gateway_id                 = lookup(route.value, "gateway_id", null)
      nat_gateway_id             = lookup(route.value, "nat_gateway_id", null)
      network_interface_id       = lookup(route.value, "network_interface_id", null)
      transit_gateway_id         = lookup(route.value, "transit_gateway_id", null)
      vpc_endpoint_id            = lookup(route.value, "vpc_endpoint_id", null)
      vpc_peering_connection_id  = lookup(route.value, "vpc_peering_connection_id", null)
    }
  }

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
    prevent_destroy = true
    ignore_changes  = [route]
  }
}
