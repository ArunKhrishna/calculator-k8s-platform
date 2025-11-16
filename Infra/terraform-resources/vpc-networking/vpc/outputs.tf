# VPC Outputs
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.glad_vpc.id
}

output "vpc_arn" {
  description = "VPC ARN"
  value       = aws_vpc.glad_vpc.arn
}

output "vpc_cidr_block" {
  description = "VPC CIDR block"
  value       = aws_vpc.glad_vpc.cidr_block
}

output "vpc_main_route_table_id" {
  description = "Main route table ID"
  value       = aws_vpc.glad_vpc.main_route_table_id
}

output "vpc_default_network_acl_id" {
  description = "Default network ACL ID"
  value       = aws_vpc.glad_vpc.default_network_acl_id
}

output "vpc_default_security_group_id" {
  description = "Default security group ID"
  value       = aws_vpc.glad_vpc.default_security_group_id
}

output "vpc_default_route_table_id" {
  description = "Default route table ID"
  value       = aws_vpc.glad_vpc.default_route_table_id
}

output "vpc_owner_id" {
  description = "VPC owner ID"
  value       = aws_vpc.glad_vpc.owner_id
}

output "vpc_enable_dns_hostnames" {
  description = "Whether DNS hostnames are enabled"
  value       = aws_vpc.glad_vpc.enable_dns_hostnames
}

output "vpc_enable_dns_support" {
  description = "Whether DNS support is enabled"
  value       = aws_vpc.glad_vpc.enable_dns_support
}

output "vpc_details" {
  description = "Complete VPC details"
  value = {
    id                        = aws_vpc.glad_vpc.id
    arn                       = aws_vpc.glad_vpc.arn
    cidr_block                = aws_vpc.glad_vpc.cidr_block
    instance_tenancy          = aws_vpc.glad_vpc.instance_tenancy
    enable_dns_hostnames      = aws_vpc.glad_vpc.enable_dns_hostnames
    enable_dns_support        = aws_vpc.glad_vpc.enable_dns_support
    main_route_table_id       = aws_vpc.glad_vpc.main_route_table_id
    default_network_acl_id    = aws_vpc.glad_vpc.default_network_acl_id
    default_security_group_id = aws_vpc.glad_vpc.default_security_group_id
    default_route_table_id    = aws_vpc.glad_vpc.default_route_table_id
    owner_id                  = aws_vpc.glad_vpc.owner_id
  }
}


