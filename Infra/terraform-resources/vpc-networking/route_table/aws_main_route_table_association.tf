# # Get the main route table
# locals {
#   main_route_table = {
#     for k, v in var.route_tables : k => v
#     if v.is_main
#   }
# }

# resource "aws_main_route_table_association" "ac9_main_route_table_association" {
#   for_each = local.main_route_table

#   vpc_id         = var.vpc_id
#   route_table_id = aws_route_table.ac9_route_table[each.key].id

#   depends_on = [aws_route_table.glad]
# }
