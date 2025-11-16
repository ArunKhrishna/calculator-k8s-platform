resource "aws_rds_cluster" "rds_cluster" {
  cluster_identifier                    = var.db_cluster_name
  engine                                = "aurora-postgresql"
  engine_version                        = var.engine_version
  engine_mode                           = "provisioned"
  database_name                         = "postgres"
  master_username                       = "postgres"
  master_password                       = var.db_password
  db_subnet_group_name                  = aws_db_subnet_group.rds_subnet_group.name
  availability_zones                    = var.cluster_availability_zones
  backup_retention_period               = var.backup_retention_period
  vpc_security_group_ids                = [var.security_group_id]
  skip_final_snapshot                   = var.skip_final_snapshot
  final_snapshot_identifier             = var.skip_final_snapshot ? null : "${var.db_cluster_name}-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"
  storage_encrypted                     = true
  deletion_protection                   = var.deletion_protection
  performance_insights_enabled          = true
  monitoring_interval                   = 60
  monitoring_role_arn                   = var.monitoring_role_arn
  performance_insights_retention_period = 7
  preferred_backup_window               = "03:00-04:00"
  preferred_maintenance_window          = "sun:04:00-sun:05:00"
  db_cluster_parameter_group_name       = aws_rds_cluster_parameter_group.rds_cluster_parameter_group.name
  engine_lifecycle_support              = "open-source-rds-extended-support-disabled"
  enabled_cloudwatch_logs_exports       = ["postgresql"]

  tags = {
    Name        = var.db_cluster_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Project     = "GLAD"
  }

  lifecycle {
    ignore_changes = [master_password]
  }

  depends_on = [
    aws_db_subnet_group.rds_subnet_group,
    aws_rds_cluster_parameter_group.rds_cluster_parameter_group,
    aws_db_parameter_group.rds_instance_parameter_group
  ]
}