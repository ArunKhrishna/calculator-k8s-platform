locals {
  ingress_rules = flatten([
    for sg_key, sg_value in var.security_groups : [
      for idx, rule in sg_value.ingress_rules : {
        sg_key                   = sg_key
        rule_key                 = "${sg_key}-ingress-${idx}"
        description              = lookup(rule, "description", null)
        from_port                = rule.from_port
        to_port                  = rule.to_port
        protocol                 = rule.protocol
        cidr_blocks              = lookup(rule, "cidr_blocks", null)
        ipv6_cidr_blocks         = lookup(rule, "ipv6_cidr_blocks", null)
        source_security_group_id = lookup(rule, "source_security_group_id", null)
        self                     = lookup(rule, "self", null)
      }
    ]
  ])
  
  egress_rules = flatten([
    for sg_key, sg_value in var.security_groups : [
      for idx, rule in sg_value.egress_rules : {
        sg_key                   = sg_key
        rule_key                 = "${sg_key}-egress-${idx}"
        description              = lookup(rule, "description", null)
        from_port                = rule.from_port
        to_port                  = rule.to_port
        protocol                 = rule.protocol
        cidr_blocks              = lookup(rule, "cidr_blocks", null)
        ipv6_cidr_blocks         = lookup(rule, "ipv6_cidr_blocks", null)
        source_security_group_id = lookup(rule, "source_security_group_id", null)
        self                     = lookup(rule, "self", null)
      }
    ]
  ])
}

resource "aws_security_group_rule" "ingress" {
  for_each = {
    for rule in local.ingress_rules : rule.rule_key => rule
  }

  type              = "ingress"
  from_port         = each.value.from_port
  to_port           = each.value.to_port
  protocol          = each.value.protocol
  description       = each.value.description
  security_group_id = aws_security_group.ac9_security_group[each.value.sg_key].id

  cidr_blocks              = each.value.source_security_group_id != null || each.value.self == true ? null : each.value.cidr_blocks
  ipv6_cidr_blocks         = each.value.source_security_group_id != null || each.value.self == true ? null : each.value.ipv6_cidr_blocks
  source_security_group_id = each.value.source_security_group_id
  self                     = each.value.self == true ? true : null

  depends_on = [aws_security_group.ac9_security_group]
}

resource "aws_security_group_rule" "egress" {
  for_each = {
    for rule in local.egress_rules : rule.rule_key => rule
  }

  type              = "egress"
  from_port         = each.value.from_port
  to_port           = each.value.to_port
  protocol          = each.value.protocol
  description       = each.value.description
  security_group_id = aws_security_group.ac9_security_group[each.value.sg_key].id

  cidr_blocks              = each.value.source_security_group_id != null || each.value.self == true ? null : each.value.cidr_blocks
  ipv6_cidr_blocks         = each.value.source_security_group_id != null || each.value.self == true ? null : each.value.ipv6_cidr_blocks
  source_security_group_id = each.value.source_security_group_id
  self                     = each.value.self == true ? true : null

  depends_on = [aws_security_group.ac9_security_group]
}