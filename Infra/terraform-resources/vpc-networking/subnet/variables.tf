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

# for the map(object) type:
# key ( string ) => value ( object with fields)
# "subnet-1"   → {
#                  cidr_block        = "10.0.0.0/24"
#                  availability_zone = "us-east-1a"
#                  subnet_type       = "private"
#                }
# "subnet-2"   → {
#                  cidr_block        = "10.0.1.0/24"
#                  availability_zone = "us-east-1b"
#                  subnet_type       = "public"
#                }


variable "subnets" {
  description = "Map of subnet configurations"
  type = map(object({
    cidr_block              = string
    availability_zone       = string
    map_public_ip_on_launch = bool
    subnet_type             = string # "public", "private", or "database"
    tags                    = optional(map(string))
  }))
  default = {}
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {}
}

variable "private_subnet_tags" {
  description = "Private subnet tags"
  type        = map(string)
  default     = {}
}

variable "public_subnet_tags" {
  description = "Public subnet tags"
  type        = map(string)
  default     = {}
}
