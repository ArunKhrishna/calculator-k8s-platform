variable "environment" {
  description = "Environment name (qa, sb, prod, dev)"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID to attach the Internet Gateway"
  type        = string
}

variable "name" {
  description = "Name of the Internet Gateway"
  type        = string
}

variable "tags" {
  description = "Additional tags for the Internet Gateway"
  type        = map(string)
  default     = {}
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}