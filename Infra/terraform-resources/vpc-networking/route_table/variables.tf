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

variable "route_tables" {
  description = "Map of route table configurations"
  type = map(object({
    name = string
    routes = list(object({
      cidr_block                = optional(string)
      ipv6_cidr_block           = optional(string)
      destination_prefix_list_id = optional(string)
      gateway_id                = optional(string)
      nat_gateway_id            = optional(string)
      network_interface_id      = optional(string)
      transit_gateway_id        = optional(string)
      vpc_endpoint_id           = optional(string)
      vpc_peering_connection_id = optional(string)
    }))
    subnet_associations = list(string)
    is_main             = bool
    tags                = map(string)
  }))
  default = {}
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}

