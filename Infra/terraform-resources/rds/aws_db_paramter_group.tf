resource "aws_db_parameter_group" "rds_instance_parameter_group" {
  name        = "${var.environment}-glad-instance"
  family      = "aurora-postgresql16"
  description = "Parameter group for GLAD instance"

  tags = {
    Name        = "${var.environment}-glad-instance-pg"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }

  lifecycle {
    create_before_destroy = true
  }
}