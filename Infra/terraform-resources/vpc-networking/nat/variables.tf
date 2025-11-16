variable "environment" {
  description = "Environment name (qa, sb, prod, dev)"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "subnet_id" {
  description = "Subnet ID for the NAT Gateway (must be a public subnet)"
  type        = string
}

variable "allocation_id" {
  description = "Elastic IP allocation ID for the NAT Gateway"
  type        = string
}

variable "name" {
  description = "Name of the NAT Gateway"
  type        = string
}

variable "connectivity_type" {
  description = "Connectivity type for NAT Gateway (public or private)"
  type        = string
  default     = "public"
}

variable "tags" {
  description = "Additional tags for the NAT Gateway"
  type        = map(string)
  default     = {}
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}
