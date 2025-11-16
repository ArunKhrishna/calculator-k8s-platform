resource "aws_rds_cluster_instance" "primary" {
  identifier                            = "${var.environment}-glad-instance-primary"
  cluster_identifier                    = aws_rds_cluster.rds_cluster.id
  instance_class                        = var.db_instance_class
  engine                                = aws_rds_cluster.rds_cluster.engine
  engine_version                        = aws_rds_cluster.rds_cluster.engine_version
  availability_zone                     = var.primary_availability_zone
  db_subnet_group_name                  = aws_db_subnet_group.rds_subnet_group.name
  auto_minor_version_upgrade            = false
  performance_insights_enabled          = true
  performance_insights_retention_period = 7
  monitoring_interval                   = 60
  db_parameter_group_name               = aws_db_parameter_group.rds_instance_parameter_group.name
  publicly_accessible                   = false
  monitoring_role_arn                   = var.monitoring_role_arn

  tags = {
    Name        = "${var.environment}-glad-instance-primary"
    Environment = var.environment
    ManagedBy   = "Terraform"
    Role        = "Primary"
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_rds_cluster.rds_cluster,
    aws_db_parameter_group.rds_instance_parameter_group
  ]
}

resource "aws_rds_cluster_instance" "replica" {
  count = var.read_replica_enabled ? 1 : 0

  identifier                            = "${var.environment}-glad-instance-replica"
  cluster_identifier                    = aws_rds_cluster.rds_cluster.id
  instance_class                        = var.db_instance_class
  engine                                = aws_rds_cluster.rds_cluster.engine
  engine_version                        = aws_rds_cluster.rds_cluster.engine_version
  availability_zone                     = var.secondary_availability_zone
  db_subnet_group_name                  = aws_db_subnet_group.rds_subnet_group.name
  auto_minor_version_upgrade            = false
  performance_insights_enabled          = true
  performance_insights_retention_period = 7
  monitoring_interval                   = 60
  db_parameter_group_name               = aws_db_parameter_group.rds_instance_parameter_group.name
  publicly_accessible                   = false
  monitoring_role_arn                   = var.monitoring_role_arn

  tags = {
    Name        = "${var.environment}-glad-instance-replica"
    Environment = var.environment
    ManagedBy   = "Terraform"
    Role        = "ReadReplica"
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_rds_cluster.rds_cluster,
    aws_rds_cluster_instance.primary
  ]
}