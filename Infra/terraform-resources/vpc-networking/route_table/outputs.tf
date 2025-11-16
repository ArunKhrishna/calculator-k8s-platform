# Route Table Outputs
output "route_table_ids" {
  description = "Map of route table IDs"
  value       = { for k, rt in aws_route_table.ac9_route_table : k => rt.id }
}

output "route_table_arns" {
  description = "Map of route table ARNs"
  value       = { for k, rt in aws_route_table.ac9_route_table : k => rt.arn }
}

output "route_table_owner_ids" {
  description = "Map of route table owner IDs"
  value       = { for k, rt in aws_route_table.ac9_route_table : k => rt.owner_id }
}

output "route_table_association_ids" {
  description = "Map of route table association IDs"
  value       = { for k, assoc in aws_route_table_association.ac9_route_table_association : k => assoc.id }
}

# output "main_route_table_association_ids" {
#   description = "Map of main route table association IDs"
#   value       = { for k, assoc in aws_main_route_table_association.ac9_route_table : k => assoc.id }
# }

# Public and Private Route Table IDs (for common use)
output "public_route_table_ids" {
  description = "List of public route table IDs"
  value = [
    for k, rt in aws_route_table.ac9_route_table : rt.id
    if can(regex("public", lower(k)))
  ]
}

output "private_route_table_ids" {
  description = "List of private route table IDs"
  value = [
    for k, rt in aws_route_table.ac9_route_table : rt.id
    if can(regex("private", lower(k)))
  ]
}

output "route_table_details" {
  description = "Complete route table details"
  value = {
    for k, rt in aws_route_table.ac9_route_table : k => {
      id       = rt.id
      arn      = rt.arn
      vpc_id   = rt.vpc_id
      owner_id = rt.owner_id
      tags     = rt.tags
    }
  }
}
