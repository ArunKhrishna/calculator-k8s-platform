variable "environment" {
  description = "Environment name"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "eks_cluster_role_name" {
  description = "Name of the EKS cluster IAM role"
  type        = string
}

variable "eks_node_group_role_name" {
  description = "Name of the EKS node group IAM role"
  type        = string
}

variable "tags" {
  description = "Common tags"
  type        = map(string)
  default     = {}
}