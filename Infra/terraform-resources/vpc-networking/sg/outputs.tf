output "security_group_ids" {
  description = "Map of security group names to their IDs"
  value = {
    for k, v in aws_security_group.ac9_security_group : k => v.id
  }
}

output "security_group_arns" {
  description = "Map of security group names to their ARNs"
  value = {
    for k, v in aws_security_group.ac9_security_group : k => v.arn
  }
}

output "rds_security_group_id" {
  description = "ID of the RDS security group"
  value       = try(aws_security_group.ac9_security_group["qa_glad_rds"].id, null)
}

output "rds_security_group_arn" {
  description = "ARN of the RDS security group"
  value       = try(aws_security_group.ac9_security_group["qa_glad_rds"].arn, null)
}

output "default_security_group_id" {
  description = "ID of the default security group"
  value       = try(aws_security_group.ac9_security_group["qa_default"].id, null)
}

output "default_security_group_arn" {
  description = "ARN of the default security group"
  value       = try(aws_security_group.ac9_security_group["qa_default"].arn, null)
}