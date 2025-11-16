# Flatten subnet associations for all route tables
locals {
  subnet_associations = flatten([
    for rt_key, rt_value in var.route_tables : [
      for subnet_id in rt_value.subnet_associations : {
        route_table_key = rt_key
        subnet_id       = subnet_id
        association_key = "${rt_key}-${subnet_id}"
      }
    ]
  ])
}

resource "aws_route_table_association" "ac9_route_table_association" {
  for_each = {
    for assoc in local.subnet_associations : assoc.association_key => assoc
  }

  subnet_id      = each.value.subnet_id
  route_table_id = aws_route_table.ac9_route_table[each.value.route_table_key].id

  depends_on = [aws_route_table.ac9_route_table]
}
