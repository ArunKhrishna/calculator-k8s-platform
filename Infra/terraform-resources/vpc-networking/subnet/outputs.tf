# All Subnet Outputs


# { for k, subnet in aws_subnet.ac9_subnet : k => subnet.id }
# │  │   │  │       │                        │    │
# │  │   │  │       │                        │    └─ Value expression
# │  │   │  │       │                        └────── Key expression
# │  │   │  │       └───────────────────────────── Collection to iterate
# │  │   │  └───────────────────────────────────── Iterator variable (each item)
# │  │   └──────────────────────────────────────── Iterator variable (each key)
# │  └──────────────────────────────────────────── Loop keyword
# └─────────────────────────────────────────────── Map output (curly braces)


#here, k acts as the unique identifier for each subnet in the map aws_subnet.ac9_subnet annd subnet represents the actual subnet resource object. The expression constructs a new map where each key is the subnet's unique identifier (k) and the corresponding value is the subnet's ID (subnet.id). acts as the resource objject
output "subnet_ids" {
  description = "Map of subnet IDs"
  value       = { for k, subnet in aws_subnet.ac9_subnet : k => subnet.id }
}

output "subnet_arns" {
  description = "Map of subnet ARNs"
  value       = { for k, subnet in aws_subnet.ac9_subnet : k => subnet.arn }
}

output "subnet_cidr_blocks" {
  description = "Map of subnet CIDR blocks"
  value       = { for k, subnet in aws_subnet.ac9_subnet : k => subnet.cidr_block }
}

output "subnet_availability_zones" {
  description = "Map of subnet availability zones"
  value       = { for k, subnet in aws_subnet.ac9_subnet : k => subnet.availability_zone }
}

# Public Subnets
output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value = [
    for k, subnet in aws_subnet.ac9_subnet : subnet.id
    if can(regex("public", lower(k)))
  ]
}

# # Loop iterations:
# Iteration 1:
#   k      = "qa-private-ap-south-1a"
#   subnet = <subnet resource object for private-1a>
#   Result = "qa-private-ap-south-1a" => subnet.id
#            "qa-private-ap-south-1a" => "subnet-0a1b2c3d"

output "public_subnet_cidr_blocks" {
  description = "List of public subnet CIDR blocks"
  value = [
    for k, subnet in aws_subnet.ac9_subnet : subnet.cidr_block
    if can(regex("public", lower(k)))
  ]
}

# Private Subnets
output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value = [
    for k, subnet in aws_subnet.ac9_subnet : subnet.id
    if can(regex("private", lower(k)))
  ]
}


#can() acts as an error handling function. It attempts to evaluate the expression inside it and returns true if the expression is valid and does not produce an error. If the expression results in an error, can() returns false instead of causing the entire Terraform operation to fail.
output "private_subnet_cidr_blocks" {
  description = "List of private subnet CIDR blocks"
  value = [
    for k, subnet in aws_subnet.ac9_subnet : subnet.cidr_block
    if can(regex("private", lower(k)))
  ]
}

# Database Subnets
output "database_subnet_ids" {
  description = "List of database subnet IDs"
  value = [
    for k, subnet in aws_subnet.ac9_subnet : subnet.id
    if can(regex("database", lower(k)))
  ]
}

# Subnet Details
output "subnet_details" {
  description = "Complete subnet details"
  value = {
    for k, subnet in aws_subnet.ac9_subnet : k => {
      id                      = subnet.id
      arn                     = subnet.arn
      cidr_block              = subnet.cidr_block
      availability_zone       = subnet.availability_zone
      map_public_ip_on_launch = subnet.map_public_ip_on_launch
    }
  }
}
