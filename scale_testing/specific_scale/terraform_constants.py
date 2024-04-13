
TERRAFORM_PROVIDER = """
terraform {
  required_version = ">= 0.14.0"
  required_providers {
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "1.49.0"
    }
  }
}

provider "openstack" {
  user_name   = "%(username)s"
  tenant_name = "admin"
  password    = "%(password)s"
  auth_url    = "http://%(ip)s:5000"
  region      = "regionOne"
}

"""

ADMIN_TENANT_TERRAFORM = """
data "openstack_identity_project_v3" "admin" {
  name = "admin"
}
"""

TENANT_TERRAFORM = """
resource "openstack_identity_project_v3" "%(project)s" {
  name        = "%(name_alias)s"
  description = "%(description)s project"
}

resource "openstack_identity_user_v3" "user_1" {
  default_project_id = openstack_identity_project_v3.%(project)s.id
  name               = "%(project)s-user"
  description        = "A %(project)s user"

  password = "noir0123"

  ignore_change_password_upon_first_use = true
}
"""

NETWORK_TERRAFORM = """
resource "openstack_networking_network_v2" "%(name)s" {
  name           = "%(name_alias)s"
  admin_state_up = "true"
  tenant_id      = openstack_identity_project_v3.%(project)s.id
}
"""

EXTERNAL_NETWORK_TERRAFORM = """
data "openstack_networking_network_v2" "%(name)s" {
  name           = "%(name_alias)s"
  external       = "true"
  tenant_id      = data.openstack_identity_project_v3.%(project)s.id
}
// create command: openstack network create --external --share %(name)s
// delete command: openstack network delete %(name)s
"""

ROUTER_GW_TERRAFORM = """
resource "openstack_networking_router_v2" "%(name)s" {
  name                = "%(name_alias)s"
  admin_state_up      = "true"
  tenant_id           = openstack_identity_project_v3.%(project)s.id
  external_network_id = data.openstack_networking_network_v2.%(external_network)s.id
}
"""

ROUTER_TERRAFORM = """
resource "openstack_networking_router_v2" "%(name)s" {
  name           = "%(name_alias)s"
  admin_state_up = "true"
  tenant_id      = openstack_identity_project_v3.%(project)s.id
}
"""

ROUTER_INTERFACE_TERRAFORM = """
resource "openstack_networking_router_interface_v2" "%(router_if_name)s" {
  router_id = openstack_networking_router_v2.%(name)s.id
  subnet_id = openstack_networking_subnet_v2.%(subnet)s.id
}
"""

SUBNET_TERRAFORM = """
resource "openstack_networking_subnet_v2" "%(name)s" {
  name       = "%(name_alias)s"
  cidr       = "%(cidr)s"
  network_id = openstack_networking_network_v2.%(network)s.id
  tenant_id  = openstack_identity_project_v3.%(project)s.id
}
"""

SUBNET_FROM_POOL_TERRAFORM = """
resource "openstack_networking_subnet_v2" "%(name)s" {
  name          = "%(name_alias)s"
  cidr          = "%(cidr)s"
  subnetpool_id = data.openstack_networking_subnetpool_v2.%(subnetpool_id)s.id
  network_id    = openstack_networking_network_v2.%(network)s.id
  tenant_id     = openstack_identity_project_v3.%(project)s.id
}
"""

ADDRESS_SCOPE_TERRAFORM = """
resource "openstack_networking_addressscope_v2" "%(name)s" {
  name       = "%(name_alias)s"
  tenant_id  = openstack_identity_project_v3.%(project)s.id
  ip_version = 4
}
"""

ADDRESS_SCOPE_SHARED_TERRAFORM = """
data "openstack_networking_addressscope_v2" "%(name)s" {
  name       = "%(name_alias)s"
  shared     = true
  ip_version = 4
}
// create command: openstack address scope create --share %(name)s
// delete command: openstack address scope delete %(name)s
"""

SUBNET_POOL_SHARED_TERRAFORM = """
data "openstack_networking_subnetpool_v2" "%(name)s" {
  name             = "%(name_alias)s"
  shared           = true
  //prefixes         = ["%(cidrs)s"]
  address_scope_id = data.openstack_networking_addressscope_v2.%(as_name)s.id
}
// create command: openstack subnet pool create --pool-prefix %(cidrs)s --default-prefix-length %(prefixlen)s --share --address-scope %(as_name)s %(name)s
// delete command: openstack subnet pool delete %(name)s
"""

SECURITY_GROUP_TERRAFORM = """
resource "openstack_networking_secgroup_v2" "%(name)s" {
  name        = "%(name_alias)s"
  tenant_id   = openstack_identity_project_v3.%(project)s.id
}
"""

SECURITY_GROUP_EXISTING_TERRAFORM = """
data "openstack_networking_secgroup_v2" "%(name)s" {
  name        = "%(name_alias)s"
  tenant_id   = openstack_identity_project_v3.%(project)s.id
}
"""

SECURITY_GROUP_RULE_TERRAFORM_PORTS_R_SG = """
resource "openstack_networking_secgroup_rule_v2" "%(name)s" {
  depends_on = [ %(tf_type)s.openstack_networking_secgroup_v2.%(sec_group_id)s ]
  direction         = "%(direction)s"
  ethertype         = "%(ethertype)s"
  protocol          = "%(protocol)s"
  port_range_min    = %(min_port)s
  port_range_max    = %(max_port)s
  remote_group_id   = %(tf_type)s.openstack_networking_secgroup_v2.%(remote_group_id)s.id
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = %(tf_type)s.openstack_networking_secgroup_v2.%(sec_group_id)s.id
}
"""

SECURITY_GROUP_RULE_TERRAFORM_PORTS_R_IP = """
resource "openstack_networking_secgroup_rule_v2" "%(name)s" {
  depends_on = [ %(tf_type)s.openstack_networking_secgroup_v2.%(sec_group_id)s ]
  direction         = "%(direction)s"
  ethertype         = "%(ethertype)s"
  protocol          = "%(protocol)s"
  port_range_min    = %(min_port)s
  port_range_max    = %(max_port)s
  remote_ip_prefix  = "%(remote_ip_prefix)s"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = %(tf_type)s.openstack_networking_secgroup_v2.%(sec_group_id)s.id
}
"""

SECURITY_GROUP_RULE_TERRAFORM_NO_PORTS_R_SG = """
resource "openstack_networking_secgroup_rule_v2" "%(name)s" {
  depends_on = [ %(tf_type)s.openstack_networking_secgroup_v2.%(sec_group_id)s ]
  direction         = "%(direction)s"
  ethertype         = "%(ethertype)s"
  protocol          = "%(protocol)s"
  remote_group_id   = %(tf_type)s.openstack_networking_secgroup_v2.%(remote_group_id)s.id
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = %(tf_type)s.openstack_networking_secgroup_v2.%(sec_group_id)s.id
}
"""

SECURITY_GROUP_RULE_TERRAFORM_NO_PORTS_R_IP = """
resource "openstack_networking_secgroup_rule_v2" "%(name)s" {
  depends_on = [ %(tf_type)s.openstack_networking_secgroup_v2.%(sec_group_id)s ]
  direction         = "%(direction)s"
  ethertype         = "%(ethertype)s"
  protocol          = "%(protocol)s"
  remote_ip_prefix  = "%(remote_ip_prefix)s"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = %(tf_type)s.openstack_networking_secgroup_v2.%(sec_group_id)s.id
}
"""

SECURITY_GROUP_RULE_TERRAFORM_NO_PROTO_R_SG = """
resource "openstack_networking_secgroup_rule_v2" "%(name)s" {
  depends_on = [ %(tf_type)s.openstack_networking_secgroup_v2.%(sec_group_id)s ]
  direction         = "%(direction)s"
  ethertype         = "%(ethertype)s"
  remote_group_id   = %(tf_type)s.openstack_networking_secgroup_v2.%(remote_group_id)s.id
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = %(tf_type)s.openstack_networking_secgroup_v2.%(sec_group_id)s.id
}
"""

SECURITY_GROUP_RULE_TERRAFORM_NO_PROTO_R_IP = """
resource "openstack_networking_secgroup_rule_v2" "%(name)s" {
  depends_on = [ %(tf_type)s.openstack_networking_secgroup_v2.%(sec_group_id)s ]
  direction         = "%(direction)s"
  ethertype         = "%(ethertype)s"
  remote_ip_prefix  = "%(remote_ip_prefix)s"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = %(tf_type)s.openstack_networking_secgroup_v2.%(sec_group_id)s.id
}
"""

PORT_PART1_TERRAFORM = """
resource "openstack_networking_port_v2" "%(name)s" {
  name               = "%(name)s"
  network_id         = openstack_networking_network_v2.net_%(network_id)s.id
  device_id          = "%(device_id)s"
  device_owner       = "%(device_owner)s"
  admin_state_up     = "%(admin_state_up)s" """

PORT_NO_SECGROUP_TERRAFORM = """
  no_security_groups"""

PORT_START_SECGROUP_TERRAFORM = """
  security_group_ids = ["""

PORT_SECGROUP_TERRAFORM = """
    openstack_networking_secgroup_v2.sg_%s.id,"""

PORT_DEFAULT_SECGROUP_TERRAFORM = """
    data.openstack_networking_secgroup_v2.sg_%s.id,"""

PORT_LAST_SECGROUP_TERRAFORM = """
    openstack_networking_secgroup_v2.sg_%s.id
  ]"""

PORT_DEFAULT_LAST_SECGROUP_TERRAFORM = """
    data.openstack_networking_secgroup_v2.sg_%s.id
  ]"""

PORT_FIXED_IP_TERRAFORM ="""
  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.sub_%(subnet_id)s.id
    ip_address = "%(ip_address)s"
  }"""

PORT_AAPS_TERRAFORM = """
  allowed_address_pairs {
      ip_address   = "%(ip_address)s"
  }"""

PORT_PART2_TERRAFORM = """
  tenant_id          = openstack_identity_project_v3.prj_%(project_id)s.id
  binding {
    host_id   = "%(binding_host_id)s"
  }
}
"""
