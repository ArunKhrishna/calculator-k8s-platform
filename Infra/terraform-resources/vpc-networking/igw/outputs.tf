# Internet Gateway Outputs
output "igw_id" {
  description = "Internet Gateway ID"
  value       = aws_internet_gateway.ac9_internet_gateway.id
}

output "igw_arn" {
  description = "Internet Gateway ARN"
  value       = aws_internet_gateway.ac9_internet_gateway.arn
}

output "igw_owner_id" {
  description = "Internet Gateway owner ID"
  value       = aws_internet_gateway.ac9_internet_gateway.owner_id
}

output "igw_vpc_id" {
  description = "VPC ID attached to the Internet Gateway"
  value       = aws_internet_gateway.ac9_internet_gateway.vpc_id
}

output "igw_details" {
  description = "Complete Internet Gateway details"
  value = {
    id       = aws_internet_gateway.ac9_internet_gateway.id
    arn      = aws_internet_gateway.ac9_internet_gateway.arn
    vpc_id   = aws_internet_gateway.ac9_internet_gateway.vpc_id
    owner_id = aws_internet_gateway.ac9_internet_gateway.owner_id
    tags     = aws_internet_gateway.ac9_internet_gateway.tags
  }
}
