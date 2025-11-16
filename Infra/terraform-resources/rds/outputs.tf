output "cluster_id" {
  description = "RDS cluster identifier"
  value       = aws_rds_cluster.rds_cluster.id
}

output "cluster_arn" {
  description = "RDS cluster ARN"
  value       = aws_rds_cluster.rds_cluster.arn
}

output "cluster_endpoint" {
  description = "Cluster endpoint"
  value       = aws_rds_cluster.rds_cluster.endpoint
}

output "cluster_reader_endpoint" {
  description = "Cluster reader endpoint"
  value       = aws_rds_cluster.rds_cluster.reader_endpoint
}

output "cluster_port" {
  description = "Database port"
  value       = aws_rds_cluster.rds_cluster.port
}

output "cluster_database_name" {
  description = "Database name"
  value       = aws_rds_cluster.rds_cluster.database_name
}

output "cluster_master_username" {
  description = "Master username"
  value       = aws_rds_cluster.rds_cluster.master_username
  sensitive   = true
}

output "primary_instance_id" {
  description = "Primary instance ID"
  value       = aws_rds_cluster_instance.primary.id
}

output "primary_instance_endpoint" {
  description = "Primary instance endpoint"
  value       = aws_rds_cluster_instance.primary.endpoint
}

output "replica_instance_id" {
  description = "Replica instance ID"
  value       = var.read_replica_enabled ? aws_rds_cluster_instance.replica[0].id : null
}

output "connection_string" {
  description = "PostgreSQL connection string"
  value       = "postgresql://postgres@${aws_rds_cluster.rds_cluster.endpoint}:${aws_rds_cluster.rds_cluster.port}/${aws_rds_cluster.rds_cluster.database_name}"
  sensitive   = true
}