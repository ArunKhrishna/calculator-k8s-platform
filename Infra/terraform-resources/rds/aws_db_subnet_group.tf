resource "aws_db_subnet_group" "rds_subnet_group" {
  name        = "${var.environment}-glad-subnet-group"
  description = "Subnet group for GLAD RDS instance"
  subnet_ids  = var.private_subnet_ids

  tags = {
    Name        = "${var.environment}-glad-subnet-group"
    Environment = var.environment
    ManagedBy   = "Terraform"
    Project     = "GLAD"
  }
}