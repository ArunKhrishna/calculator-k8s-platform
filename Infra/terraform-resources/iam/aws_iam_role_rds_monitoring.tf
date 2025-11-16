resource "aws_iam_role" "rds_monitoring" {
  name               = "rds-monitoring-role"
  assume_role_policy = data.aws_iam_policy_document.rds_monitoring_assume.json

  tags = {
    Name        = "rds-monitoring-role"
    Environment = var.environment
    ManagedBy   = "Terraform"
    Purpose     = "RDS Enhanced Monitoring"
  }
}

data "aws_iam_policy_document" "rds_monitoring_assume" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["monitoring.rds.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  role       = aws_iam_role.rds_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}