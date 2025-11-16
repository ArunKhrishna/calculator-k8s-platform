variable "environment" {
  description = "Environment name (qa, sb, prod)"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "account_id" {
  description = "AWS Account ID"
  type        = string
  default     = "183631346081"
}

# Elastic IP Configurations
variable "elastic_ips" {
  description = "Map of Elastic IP configurations"
  type = map(object({
    name                 = string
    domain               = string
    network_interface_id = optional(string)
    instance_id          = optional(string)
    associate_with_nat   = optional(bool, false)
    tags                 = optional(map(string))
  }))
  default = {}
}