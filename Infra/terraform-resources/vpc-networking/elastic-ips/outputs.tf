# Elastic IP Outputs
	output "eip_ids" {
  description = "Map of Elastic IP allocation IDs"
  value       = { for k, eip in aws_eip.ac9_eips : k => eip.id }
}

output "eip_allocation_ids" {
  description = "Map of Elastic IP allocation IDs"
  value       = { for k, eip in aws_eip.ac9_eips : k => eip.allocation_id }
}

output "eip_public_ips" {
  description = "Map of Elastic IP public IP addresses"
  value       = { for k, eip in aws_eip.ac9_eips : k => eip.public_ip }
  sensitive   = true
}

output "eip_public_dns" {
  description = "Map of Elastic IP public DNS names"
  value       = { for k, eip in aws_eip.ac9_eips : k => eip.public_dns }
  sensitive   = true
}

output "eip_private_ips" {
  description = "Map of Elastic IP private IP addresses"
  value       = { for k, eip in aws_eip.ac9_eips : k => eip.private_ip }
  sensitive   = true
}

output "eip_association_ids" {
  description = "Map of Elastic IP association IDs"
  value       = { for k, eip in aws_eip.ac9_eips : k => eip.association_id }
}

output "eip_network_interface_ids" {
  description = "Map of Elastic IP network interface IDs"
  value       = { for k, eip in aws_eip.ac9_eips : k => eip.network_interface }
}

output "eip_details" {
  description = "Detailed information about all Elastic IPs"    
  value = {
    for k, eip in aws_eip.ac9_eips : k => {
      id                   = eip.id
      allocation_id        = eip.allocation_id
      public_ip            = eip.public_ip
      private_ip           = eip.private_ip
      network_interface_id = eip.network_interface
      instance_id          = eip.instance
      domain               = eip.domain
      association_id       = eip.association_id
    }
  }
  sensitive = true
}
