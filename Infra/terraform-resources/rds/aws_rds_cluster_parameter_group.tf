resource "aws_rds_cluster_parameter_group" "rds_cluster_parameter_group" {
  name        = "${var.environment}-glad-cluster"
  family      = "aurora-postgresql16"
  description = "Parameter group for GLAD cluster"

  tags = {
    Name        = "${var.environment}-glad-cluster-pg"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }

  lifecycle {
    create_before_destroy = true
  }
}