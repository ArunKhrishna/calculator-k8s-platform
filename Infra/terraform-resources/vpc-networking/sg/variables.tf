variable "environment" {
  description = "Environment name (qa, sb, prod, dev)"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "security_groups" {
  description = "Map of security group configurations"
  type = map(object({
    name        = string
    description = string
    
    ingress_rules = list(object({
      description              = optional(string)
      from_port                = number
      to_port                  = number
      protocol                 = string
      cidr_blocks              = optional(list(string))
      ipv6_cidr_blocks         = optional(list(string))
      source_security_group_id = optional(string)
      self                     = optional(bool)
    }))
    
    egress_rules = list(object({
      description              = optional(string)
      from_port                = number
      to_port                  = number
      protocol                 = string
      cidr_blocks              = optional(list(string))
      ipv6_cidr_blocks         = optional(list(string))
      source_security_group_id = optional(string)
      self                     = optional(bool)
    }))
    
    tags = map(string)
  }))
  default = {}
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}
