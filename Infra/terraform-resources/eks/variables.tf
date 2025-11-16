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

# Cluster Configuration
variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
}

variable "cluster_version" {
  description = "Kubernetes version for EKS cluster"
  type        = string
}

variable "cluster_role_arn" {
  description = "IAM role ARN for EKS cluster"
  type        = string
}

# Network Configuration
variable "subnet_ids" {
  description = "List of subnet IDs for EKS cluster"
  type        = list(string)
}

variable "vpc_config" {
  description = "VPC configuration for EKS cluster"
  type = object({
    endpoint_private_access = bool
    endpoint_public_access  = bool
    public_access_cidrs     = list(string)
  })
  default = {
    endpoint_private_access = true
    endpoint_public_access  = true
    public_access_cidrs     = ["0.0.0.0/0"]
  }
}

# Cluster Settings
variable "enabled_cluster_log_types" {
  description = "List of control plane logging types to enable"
  type        = list(string)
  default     = ["api", "audit", "authenticator"]
}

variable "service_ipv4_cidr" {
  description = "The CIDR block to assign Kubernetes service IP addresses from"
  type        = string
  default     = "172.20.0.0/16"
}

# Node Groups Configuration
variable "node_groups" {
  description = "Map of node group configurations"
  type = map(object({
    name           = string
    ami_type       = string
    instance_types = list(string)
    desired_size   = number
    max_size       = number
    min_size       = number
    capacity_type  = optional(string, "ON_DEMAND")
    disk_size      = optional(number, 20)
    labels         = optional(map(string), {})
    taints = optional(list(object({
      key    = string
      value  = string
      effect = string
    })), [])
    enable_node_repair = optional(bool, true)
  }))
}

variable "node_role_arn" {
  description = "IAM role ARN for EKS node groups"
  type        = string
}

variable "node_group_release_version" {
  description = "AMI release version for node groups"
  type        = string
}

# Tags
variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default     = {}
}

variable "cluster_addons" {
  description = "Map of EKS add-on configurations"
  type = map(object({
    addon_name                  = string
    addon_version               = optional(string)
    resolve_conflicts_on_create = optional(string, "OVERWRITE")
    resolve_conflicts_on_update = optional(string, "OVERWRITE")
    preserve                    = optional(bool, true)
    service_account_role_arn    = optional(string)
    configuration_values        = optional(string)
  }))
  default = {}
}