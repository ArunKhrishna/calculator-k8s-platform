# NAT Gateway Outputs
output "nat_gateway_id" {
  description = "NAT Gateway ID"
  value       = aws_nat_gateway.ac9_nat_gateway.id
}

output "nat_gateway_allocation_id" {
  description = "NAT Gateway Elastic IP allocation ID"
  value       = aws_nat_gateway.ac9_nat_gateway.allocation_id
}

output "nat_gateway_subnet_id" {
  description = "Subnet ID where NAT Gateway is deployed"
  value       = aws_nat_gateway.ac9_nat_gateway.subnet_id
}

output "nat_gateway_network_interface_id" {
  description = "NAT Gateway primary network interface ID"
  value       = aws_nat_gateway.ac9_nat_gateway.network_interface_id
}

output "nat_gateway_private_ip" {
  description = "NAT Gateway private IP address"
  value       = aws_nat_gateway.ac9_nat_gateway.private_ip
}

output "nat_gateway_public_ip" {
  description = "NAT Gateway public IP address"
  value       = aws_nat_gateway.ac9_nat_gateway.public_ip
}

output "nat_gateway_details" {
  description = "Complete NAT Gateway details"
  value = {
    id                   = aws_nat_gateway.ac9_nat_gateway.id
    allocation_id        = aws_nat_gateway.ac9_nat_gateway.allocation_id
    subnet_id            = aws_nat_gateway.ac9_nat_gateway.subnet_id
    connectivity_type    = aws_nat_gateway.ac9_nat_gateway.connectivity_type
    network_interface_id = aws_nat_gateway.ac9_nat_gateway.network_interface_id
    private_ip           = aws_nat_gateway.ac9_nat_gateway.private_ip
    public_ip            = aws_nat_gateway.ac9_nat_gateway.public_ip
  }
  sensitive = true
}
