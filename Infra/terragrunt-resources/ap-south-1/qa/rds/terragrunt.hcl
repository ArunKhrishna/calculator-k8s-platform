include "root" {
  path = find_in_parent_folders("root.hcl")
}

terraform {
  source = "${get_parent_terragrunt_dir()}/../../../terraform-resources/rds"
}

dependency "vpc" {
  config_path = "../vpc-networking/vpc"
  
  mock_outputs = {
    vpc_id = "vpc-mock-12345"
  }
  mock_outputs_allowed_terraform_commands = ["validate", "plan"]
}

dependency "subnet" {
  config_path = "../vpc-networking/subnet"
  
  mock_outputs = {
    private_subnet_ids = ["subnet-mock1", "subnet-mock2"]
  }
  mock_outputs_allowed_terraform_commands = ["validate", "plan"]
}

dependency "iam" {
  config_path = "../iam"
  
  mock_outputs = {
    rds_monitoring_role_arn = "arn:aws:iam::123456789012:role/rds-monitoring-role"
  }
  mock_outputs_allowed_terraform_commands = ["validate", "plan"]
}

inputs = {
  environment = "qa"
  aws_region  = "ap-south-1"
  account_id  = get_aws_account_id()
  
  vpc_id             = dependency.vpc.outputs.vpc_id
  private_subnet_ids = dependency.subnet.outputs.private_subnet_ids
  security_group_id  = "sg-0c801604dffe81140"  # Hardcoded RDS security group
  
  db_cluster_name   = "qa-glad-aurora-cluster"
  engine_version    = "16.1"
  db_instance_class = "db.t3.medium"
  db_password       = get_env("DB_PASSWORD", "ChangeMe123!")
  
  cluster_availability_zones = ["ap-south-1a", "ap-south-1b"]
  primary_availability_zone   = "ap-south-1a"
  secondary_availability_zone = "ap-south-1b"
  
  read_replica_enabled    = false
  backup_retention_period = 7
  skip_final_snapshot     = true
  deletion_protection     = false
  
  monitoring_role_arn = dependency.iam.outputs.rds_monitoring_role_arn
  
  tags = {
    Project    = "GLAD"
    CostCenter = "Engineering"
    Team       = "DevOps"
  }
}