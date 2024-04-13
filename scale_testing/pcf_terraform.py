#
# * 1 subnetpool
#
# Master SG:
#

pcf_terraform_template = """
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
  user_name   = "admin"
  tenant_name = "admin"
  password    = "noir0123"
  auth_url    = "http://%(ip)s:5000"
  region      = "regionOne"
}

resource "openstack_identity_project_v3" "%(project)s" {
  name        = "%(project)s"
  description = "%(project)s project"
}

resource "openstack_identity_user_v3" "user_1" {
  default_project_id = openstack_identity_project_v3.%(project)s.id
  name               = "%(project)s-user"
  description        = "A %(project)s user"

  password = "noir0123"

  ignore_change_password_upon_first_use = true
}


data "openstack_networking_addressscope_v2" "interconnect_vrf" {
  name       = "interconnect_vrf"
  shared     = true
  ip_version = 4
}

resource "openstack_networking_subnetpool_v2" "pcf_subnetpool1" {
  name              = "pcf_subnetpool1"
  address_scope_id  = data.openstack_networking_addressscope_v2.interconnect_vrf.id
  prefixes          = ["192.168.128.0/17"]
  default_prefixlen = 24
}


resource "openstack_networking_network_v2" "network_1" {
  name           = "network_1"
  admin_state_up = "true"
}

resource "openstack_networking_subnet_v2" "subnet_1" {
  name          = "subnet_1"
  cidr          = "192.168.128.0/25"
  network_id    = openstack_networking_network_v2.network_1.id
  subnetpool_id = openstack_networking_subnetpool_v2.subnetpool_1.id
}

resource "openstack_networking_network_v2" "node_network" {
  name           = "node_network"
  admin_state_up = "true"
  tenant_id      = openstack_identity_project_v3.%(project)s.id
}

resource "openstack_networking_subnet_v2" "node_subnet" {
  name       = "node_subnet"
  network_id = openstack_networking_network_v2.node_network.id
  tenant_id  = openstack_identity_project_v3.%(project)s.id
  cidr       = "15.11.0.0/27"
}

resource "openstack_networking_router_v2" "router_1" {
  name           = "router_1"
  admin_state_up = "true"
  tenant_id      = openstack_identity_project_v3.%(project)s.id
  external_network_id = "72d4135b-313d-473e-b36a-28c19d23d7ef"
}

resource "openstack_networking_router_interface_v2" "int_1" {
  router_id = openstack_networking_router_v2.router_1.id
  subnet_id = openstack_networking_subnet_v2.node_subnet.id
}

resource "openstack_networking_network_v2" "pod_network" {
  name           = "pod_network"
  admin_state_up = "true"
  tenant_id      = openstack_identity_project_v3.%(project)s.id
}

resource "openstack_networking_subnet_v2" "pod_subnet" {
  name       = "pod_subnet"
  cidr       = "192.168.208.0/20"
  network_id = openstack_networking_network_v2.pod_network.id
  tenant_id  = openstack_identity_project_v3.%(project)s.id
}


resource "openstack_networking_port_v2" "vip_1" {
  name               = "vip_1"
  network_id         = openstack_networking_network_v2.node_network.id
  device_owner       = "compute:nova"
  admin_state_up     = "true"
  security_group_ids = [openstack_networking_secgroup_v2.secgroup_master.id]
  tenant_id          = openstack_identity_project_v3.%(project)s.id

  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.node_subnet.id
    ip_address = "15.11.0.5"
  }
}

resource "openstack_networking_port_v2" "vip_2" {
  name               = "vip_2"
  network_id         = openstack_networking_network_v2.node_network.id
  device_owner       = "compute:nova"
  admin_state_up     = "true"
  security_group_ids = [openstack_networking_secgroup_v2.secgroup_master.id]
  tenant_id          = openstack_identity_project_v3.%(project)s.id

  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.node_subnet.id
    ip_address = "15.11.0.7"
  }
}

resource "openstack_networking_port_v2" "bootstrap_node" {
  name               = "bootstrap_node"
  network_id         = openstack_networking_network_v2.node_network.id
  device_owner       = "compute:nova"
  admin_state_up     = "true"
  security_group_ids = [openstack_networking_secgroup_v2.secgroup_master.id]
  tenant_id          = openstack_identity_project_v3.%(project)s.id

  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.node_subnet.id
  }
  binding {
    host_id   = "overcloud-novacompute-0.localdomain"
  }
}

resource "openstack_networking_floatingip_v2" "bootstrap_fip" {
  pool       = "sauto_l3out-2"
  tenant_id  = openstack_identity_project_v3.%(project)s.id
  port_id    = openstack_networking_port_v2.bootstrap_node.id
}

resource "openstack_networking_port_v2" "master1_node" {
  depends_on = [
      resource.openstack_networking_port_v2.vip_1,
      resource.openstack_networking_port_v2.vip_2
  ]
  name               = "master1_node"
  network_id         = openstack_networking_network_v2.node_network.id
  device_owner       = "compute:nova"
  admin_state_up     = "true"
  security_group_ids = [openstack_networking_secgroup_v2.secgroup_master.id]
  tenant_id          = openstack_identity_project_v3.%(project)s.id

  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.node_subnet.id
  }
  binding {
    host_id   = "overcloud-novacompute-0.localdomain"
  }
  allowed_address_pairs {
      ip_address   = "15.11.0.5"
  }
  allowed_address_pairs {
      ip_address   = "15.11.0.7"
  }
}

resource "openstack_networking_port_v2" "master1_pod" {
  name               = "master1_pod"
  network_id         = openstack_networking_network_v2.pod_network.id
  device_owner       = "compute:nova"
  admin_state_up     = "true"
  security_group_ids = [data.openstack_networking_secgroup_v2.secgroup_default.id]
  tenant_id          = openstack_identity_project_v3.%(project)s.id

  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.pod_subnet.id
  }
  binding {
    host_id   = "overcloud-novacompute-0.localdomain"
  }
}

resource "openstack_networking_port_v2" "master2_node" {
  depends_on = [
      resource.openstack_networking_port_v2.vip_1,
      resource.openstack_networking_port_v2.vip_2
  ]
  name               = "master2_node"
  network_id         = openstack_networking_network_v2.node_network.id
  device_owner       = "compute:nova"
  admin_state_up     = "true"
  security_group_ids = [openstack_networking_secgroup_v2.secgroup_master.id]
  tenant_id          = openstack_identity_project_v3.%(project)s.id

  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.node_subnet.id
  }
  binding {
    host_id   = "overcloud-novacompute-0.localdomain"
  }
  allowed_address_pairs {
      ip_address   = "15.11.0.5"
  }
  allowed_address_pairs {
      ip_address   = "15.11.0.7"
  }
}

resource "openstack_networking_port_v2" "master2_pod" {
  name               = "master2_pod"
  network_id         = openstack_networking_network_v2.pod_network.id
  device_owner       = "compute:nova"
  admin_state_up     = "true"
  security_group_ids = [data.openstack_networking_secgroup_v2.secgroup_default.id]
  tenant_id          = openstack_identity_project_v3.%(project)s.id

  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.pod_subnet.id
  }
  binding {
    host_id   = "overcloud-novacompute-0.localdomain"
  }
}

resource "openstack_networking_port_v2" "master3_node" {
  depends_on = [
      resource.openstack_networking_port_v2.vip_1,
      resource.openstack_networking_port_v2.vip_2
  ]
  name               = "master3_node"
  network_id         = openstack_networking_network_v2.node_network.id
  device_owner       = "compute:nova"
  admin_state_up     = "true"
  security_group_ids = [openstack_networking_secgroup_v2.secgroup_master.id]
  tenant_id          = openstack_identity_project_v3.%(project)s.id

  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.node_subnet.id
  }
  binding {
    host_id   = "overcloud-novacompute-0.localdomain"
  }
  allowed_address_pairs {
      ip_address   = "15.11.0.5"
  }
  allowed_address_pairs {
      ip_address   = "15.11.0.7"
  }
}

resource "openstack_networking_port_v2" "master3_pod" {
  name               = "master3_pod"
  network_id         = openstack_networking_network_v2.pod_network.id
  device_owner       = "compute:nova"
  admin_state_up     = "true"
  security_group_ids = [data.openstack_networking_secgroup_v2.secgroup_default.id]
  tenant_id          = openstack_identity_project_v3.%(project)s.id

  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.pod_subnet.id
  }
  binding {
    host_id   = "overcloud-novacompute-0.localdomain"
  }
}


resource "openstack_networking_port_v2" "worker1_node" {
  depends_on = [
      resource.openstack_networking_port_v2.vip_1,
      resource.openstack_networking_port_v2.vip_2
  ]
  name               = "worker1_node"
  network_id         = openstack_networking_network_v2.node_network.id
  device_owner       = "compute:nova"
  admin_state_up     = "true"
  security_group_ids = [openstack_networking_secgroup_v2.secgroup_worker.id]
  tenant_id          = openstack_identity_project_v3.%(project)s.id

  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.node_subnet.id
  }
  binding {
    host_id   = "overcloud-novacompute-0.localdomain"
  }
  allowed_address_pairs {
      ip_address   = "15.11.0.5"
  }
  allowed_address_pairs {
      ip_address   = "15.11.0.7"
  }
}

resource "openstack_networking_port_v2" "worker1_pod" {
  name               = "worker1_pod"
  network_id         = openstack_networking_network_v2.pod_network.id
  device_owner       = "compute:nova"
  admin_state_up     = "true"
  security_group_ids = [openstack_networking_secgroup_v2.secgroup_worker.id]
  tenant_id          = openstack_identity_project_v3.%(project)s.id

  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.pod_subnet.id
  }
  binding {
    host_id   = "overcloud-novacompute-0.localdomain"
  }
}

resource "openstack_networking_floatingip_v2" "worker1_fip" {
  pool       = "sauto_l3out-2"
  tenant_id  = openstack_identity_project_v3.%(project)s.id
  port_id    = openstack_networking_port_v2.worker1_node.id
}

resource "openstack_networking_port_v2" "worker2_node" {
  depends_on = [
      resource.openstack_networking_port_v2.vip_1,
      resource.openstack_networking_port_v2.vip_2
  ]
  name               = "worker2_node"
  network_id         = openstack_networking_network_v2.node_network.id
  device_owner       = "compute:nova"
  admin_state_up     = "true"
  security_group_ids = [openstack_networking_secgroup_v2.secgroup_worker.id]
  tenant_id          = openstack_identity_project_v3.%(project)s.id

  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.node_subnet.id
  }
  binding {
    host_id   = "overcloud-novacompute-0.localdomain"
  }
  allowed_address_pairs {
      ip_address   = "15.11.0.5"
  }
  allowed_address_pairs {
      ip_address   = "15.11.0.7"
  }
}

resource "openstack_networking_port_v2" "worker2_pod" {
  name               = "worker2_pod"
  network_id         = openstack_networking_network_v2.pod_network.id
  device_owner       = "compute:nova"
  admin_state_up     = "true"
  security_group_ids = [openstack_networking_secgroup_v2.secgroup_worker.id]
  tenant_id          = openstack_identity_project_v3.%(project)s.id

  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.pod_subnet.id
  }
  binding {
    host_id   = "overcloud-novacompute-0.localdomain"
  }
}

resource "openstack_networking_floatingip_v2" "worker2_fip" {
  pool       = "sauto_l3out-2"
  tenant_id  = openstack_identity_project_v3.%(project)s.id
  port_id    = openstack_networking_port_v2.worker2_node.id
}
"""

