# Each OpenShift cluster ccreates the following resources:
# * 2 networks (node network and pod network)
# * 2 subnets (one subnet per network)
# * 1 router
# * 1 router gateway
# * 1 router interface (connected to node network)
# * 1 Master SG with 25 SG Rules
# * 1 Worker SG with 22 SG Rules
# * 1 bootstrap VM, configured with master SG
# * 3 master VMs, ports on node and pod networks, configured with master SG and default SG
# * 2 worker VMs, ports on node and pod networks, configured with worker SG
# * 3 FIPs (one for bootstrap and one for each worker VM's node network port)
#
# Master SG:
#
#+--------------------------------------+-------------+-----------+---------------+-------------+-----------------------+
#| ID                                   | IP Protocol | Ethertype | IP Range      | Port Range  | Remote Security Group |
#+--------------------------------------+-------------+-----------+---------------+-------------+-----------------------+
#| 085f6089-07d6-4097-b920-ca70fd8583aa | tcp         | IPv4      | 15.11.0.0/27  | 6641:6642   | None                  |
#| 1126dc76-9e53-4b82-9b46-1150730cb73a | tcp         | IPv4      | 15.11.0.0/27  | 53:53       | None                  |
#| 14beedce-c600-435c-8d67-903530f189d8 | udp         | IPv4      | 15.11.0.0/27  | 4500:4500   | None                  |
#| 19a0cf29-ad61-4cde-8a5c-9d725ae6ec2a | tcp         | IPv4      | 15.11.0.0/27  | 10250:10250 | None                  |
#| 1d8d5e94-261b-4156-a50a-b23b23e7503e | udp         | IPv4      | 15.11.0.0/27  | 30000:32767 | None                  |
#| 2fe7baf8-4a1b-4f82-9564-445e8a13a2a2 | tcp         | IPv4      | 15.11.0.0/27  | 22:22       | None                  |
#| 302e49b8-89c1-41e8-bd5e-8401e5580f23 | tcp         | IPv4      | 15.11.0.0/27  | 22623:22623 | None                  |
#| 34c390ca-cd0a-47eb-ba6b-f83c5179c7de | 112         | IPv4      | 15.11.0.0/27  |             | None                  |
#| 40a12873-0b2b-40c0-9a4d-01aae3974235 | udp         | IPv4      | 15.11.0.0/27  | 9000:9999   | None                  |
#| 43d9f7f6-4a99-4abb-a7df-798e4c1a4dd3 | tcp         | IPv4      | 0.0.0.0/0     | 22:22       | None                  |
#| 5359079d-c971-4c98-922d-c484ebd6e6ec | tcp         | IPv4      | 15.11.0.0/27  | 10257:10257 | None                  |
#| 5c85492b-b7f0-48e0-9836-03f9cd255aef | tcp         | IPv4      | 15.128.0.0/16 |             | None                  |
#| 5d82edfd-2550-4a01-a566-769bd9359899 | tcp         | IPv4      | 15.11.0.0/27  | 9000:9999   | None                  |
#| 63a366c4-f4ef-4430-a313-cebe8d07d052 | udp         | IPv4      | 15.11.0.0/27  | 4789:4789   | None                  |
#| 67cd414b-613c-4cc0-89b3-9462283af901 | udp         | IPv4      | 15.11.0.0/27  | 6081:6081   | None                  |
#| 71a49160-067e-4fa2-936c-9e730eb782c7 | udp         | IPv4      | 15.128.0.0/16 |             | None                  |
#| 83071eb9-ad16-440c-8716-5b1ff1d6b8ce | udp         | IPv4      | 15.11.0.0/27  | 500:500     | None                  |
#| 92f26e40-b145-40df-aa91-dd2b4853a738 | udp         | IPv4      | 15.11.0.0/27  | 53:53       | None                  |
#| c93e0194-af99-4d96-8e75-1f140aa47376 | None        | IPv4      | 0.0.0.0/0     |             | None                  |
#| cf84f1ff-e07a-4c3c-aa34-23db6394a4dc | icmp        | IPv4      | 0.0.0.0/0     |             | None                  |
#| d353d1ee-fd99-4d8d-907f-b9619de9540b | None        | IPv6      | ::/0          |             | None                  |
#| d3a55976-fef9-4cc9-a18f-6ba0085f74a4 | tcp         | IPv4      | 15.11.0.0/27  | 30000:32767 | None                  |
#| d46398f4-4b39-4f31-9544-a777389a2413 | tcp         | IPv4      | 15.11.0.0/27  | 10259:10259 | None                  |
#| dc5957c6-1c0f-4da7-bd8d-74597ce22a21 | tcp         | IPv4      | 0.0.0.0/0     | 6443:6443   | None                  |
#| f31eda4b-25ed-4d7e-8225-0eb2685cc69c | tcp         | IPv4      | 15.11.0.0/27  | 2379:2380   | None                  |
#+--------------------------------------+-------------+-----------+---------------+-------------+-----------------------+
#
# Worker SG:
#
# +--------------------------------------+-------------+-----------+---------------+-------------+-----------------------+
#| ID                                   | IP Protocol | Ethertype | IP Range      | Port Range  | Remote Security Group |
#+--------------------------------------+-------------+-----------+---------------+-------------+-----------------------+
#| 29dd56b5-8563-4953-8d92-b4f9845d6da3 | udp         | IPv4      | 15.11.0.0/27  | 4789:4789   | None                  |
#| 2b870c57-9868-4ccf-aea5-8ccf978e162a | tcp         | IPv4      | 15.11.0.0/27  | 22:22       | None                  |
#| 36b0c5a2-a100-4f72-8851-b1afd08ffcd2 | udp         | IPv4      | 15.11.0.0/27  | 9000:9999   | None                  |
#| 5410c1fe-bad6-49e9-889e-48e289f93d4e | None        | IPv4      | 0.0.0.0/0     |             | None                  |
#| 7f44855e-c27d-4f3e-9627-b521493d6e5d | udp         | IPv4      | 15.11.0.0/27  | 4500:4500   | None                  |
#| 8021535d-eb29-447f-8e1d-e278b8658602 | udp         | IPv4      | 15.128.0.0/16 |             | None                  |
#| b38f3711-b3d0-4401-a33b-18ce84af022f | tcp         | IPv4      | 15.11.0.0/27  | 30000:32767 | None                  |
#| b3e544b1-4ef3-43a8-9291-497f2c39bb56 | 112         | IPv4      | 15.11.0.0/27  |             | None                  |
#| ba4bb171-90d8-4290-829b-048c09675137 | tcp         | IPv4      | 0.0.0.0/0     | 443:443     | None                  |
#| bc485b9a-30e4-46fd-865f-944b331cfa55 | tcp         | IPv4      | 15.128.0.0/16 |             | None                  |
#| bf997987-decc-4e57-a5bb-b2fb132e66b5 | tcp         | IPv4      | 15.11.0.0/27  | 10250:10250 | None                  |
#| c0fa45f7-06a4-47f4-8341-c0e8b13f59ac | udp         | IPv4      | 15.11.0.0/27  | 30000:32767 | None                  |
#| c6700c36-6c75-4f1a-8690-1d9a7d5e3ee3 | tcp         | IPv4      | 0.0.0.0/0     | 80:80       | None                  |
#| c81b4c0f-2e2c-4c6e-9287-15c7106e8f58 | None        | IPv6      | ::/0          |             | None                  |
#| ce8d65bf-0286-404b-b1df-2530ee5ccfb1 | udp         | IPv4      | 15.11.0.0/27  | 6081:6081   | None                  |
#| cfdc572a-a897-4eb8-a896-fbd87a05b029 | udp         | IPv4      | 15.128.0.0/16 | 53:53       | None                  |
#| e8c8fad9-70d3-4c58-9a6d-be7d76203fbf | tcp         | IPv4      | 0.0.0.0/0     | 22:22       | None                  |
#| ec1f4a71-fa62-44da-8799-d88a0c848a3f | tcp         | IPv4      | 15.11.0.0/27  | 1936:1936   | None                  |
#| ec2007a4-8a88-4e80-89dd-46ec351d8cc1 | icmp        | IPv4      | 0.0.0.0/0     |             | None                  |
#| f554d68f-e798-4463-a942-f7faed2aba8e | udp         | IPv4      | 15.11.0.0/27  | 5353:5353   | None                  |
#| f795c2f2-0c4c-4313-b055-190fe4d20e73 | tcp         | IPv4      | 15.11.0.0/27  | 9000:9999   | None                  |
#| f94ccd5d-0416-40d2-8cb4-a900740aaf74 | udp         | IPv4      | 15.11.0.0/27  | 500:500     | None                  |
#+--------------------------------------+-------------+-----------+---------------+-------------+-----------------------+


tenant_terraform_template = """
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

data "openstack_networking_secgroup_v2" "secgroup_default" {
  name        = "default"
  tenant_id   = openstack_identity_project_v3.%(project)s.id
}

resource "openstack_networking_secgroup_rule_v2" "secgroup_rule_1" {
  direction         = "egress"
  ethertype         = "IPv4"
  remote_ip_prefix  = "172.19.0.0/16"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = data.openstack_networking_secgroup_v2.secgroup_default.id
}

resource "openstack_networking_secgroup_rule_v2" "secgroup_rule_2" {
  direction         = "egress"
  ethertype         = "IPv4"
  remote_ip_prefix  = "10.140.0.0/16"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = data.openstack_networking_secgroup_v2.secgroup_default.id
}

resource "openstack_networking_secgroup_rule_v2" "secgroup_rule_3" {
  direction         = "egress"
  ethertype         = "IPv4"
  remote_ip_prefix  = "169.254.169.254/32"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = data.openstack_networking_secgroup_v2.secgroup_default.id
}

resource "openstack_networking_secgroup_v2" "secgroup_master" {
  name        = "secgroup_master"
  description = "Security group for OpenShift master nodes"
  tenant_id   = openstack_identity_project_v3.%(project)s.id
}

resource "openstack_networking_secgroup_v2" "secgroup_worker" {
  name        = "secgroup_worker"
  description = "Security group for OpenShift worker nodes"
  tenant_id   = openstack_identity_project_v3.%(project)s.id
}

resource "openstack_networking_secgroup_rule_v2" "master_rule_1" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 6641
  port_range_max    = 6642
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_master.id
}

resource "openstack_networking_secgroup_rule_v2" "master_rule_2" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 53
  port_range_max    = 53
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_master.id
}

resource "openstack_networking_secgroup_rule_v2" "master_rule_3" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "udp"
  port_range_min    = 4500
  port_range_max    = 4500
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_master.id
}

resource "openstack_networking_secgroup_rule_v2" "master_rule_4" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 10250
  port_range_max    = 10250
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_master.id
}

resource "openstack_networking_secgroup_rule_v2" "master_rule_5" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "udp"
  port_range_min    = 30000
  port_range_max    = 32767
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_master.id
}

resource "openstack_networking_secgroup_rule_v2" "master_rule_6" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_master.id
}

resource "openstack_networking_secgroup_rule_v2" "master_rule_7" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22623
  port_range_max    = 22623
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_master.id
}

resource "openstack_networking_secgroup_rule_v2" "master_rule_8" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "112"
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_master.id
}

resource "openstack_networking_secgroup_rule_v2" "master_rule_9" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "udp"
  port_range_min    = 9000
  port_range_max    = 9999
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_master.id
}

resource "openstack_networking_secgroup_rule_v2" "master_rule_10" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  remote_ip_prefix  = "0.0.0.0/0"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_master.id
}

resource "openstack_networking_secgroup_rule_v2" "master_rule_11" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 10257
  port_range_max    = 10257
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_master.id
}

resource "openstack_networking_secgroup_rule_v2" "master_rule_12" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  remote_ip_prefix  = "15.128.0.0/16"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_master.id
}

resource "openstack_networking_secgroup_rule_v2" "master_rule_13" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 9000
  port_range_max    = 9999
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_master.id
}

resource "openstack_networking_secgroup_rule_v2" "master_rule_14" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "udp"
  port_range_min    = 4789
  port_range_max    = 4789
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_master.id
}

resource "openstack_networking_secgroup_rule_v2" "master_rule_15" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "udp"
  port_range_min    = 6081
  port_range_max    = 6081
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_master.id
}

resource "openstack_networking_secgroup_rule_v2" "master_rule_16" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "udp"
  remote_ip_prefix  = "15.128.0.0/16"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_master.id
}

resource "openstack_networking_secgroup_rule_v2" "master_rule_17" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "udp"
  port_range_min    = 500
  port_range_max    = 500
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_master.id
}

resource "openstack_networking_secgroup_rule_v2" "master_rule_18" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "udp"
  port_range_min    = 53
  port_range_max    = 53
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_master.id
}

resource "openstack_networking_secgroup_rule_v2" "master_rule_19" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "icmp"
  remote_ip_prefix  = "0.0.0.0/0"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_master.id
}

resource "openstack_networking_secgroup_rule_v2" "master_rule_20" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 30000
  port_range_max    = 32767
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_master.id
}

resource "openstack_networking_secgroup_rule_v2" "master_rule_21" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 10259
  port_range_max    = 10259
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_master.id
}

resource "openstack_networking_secgroup_rule_v2" "master_rule_22" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 6443
  port_range_max    = 6443
  remote_ip_prefix  = "0.0.0.0/0"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_master.id
}

resource "openstack_networking_secgroup_rule_v2" "master_rule_23" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 2379
  port_range_max    = 2380
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_master.id
}

resource "openstack_networking_secgroup_rule_v2" "worker_rule_1" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "udp"
  port_range_min    = 4789
  port_range_max    = 4789
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_worker.id
}

resource "openstack_networking_secgroup_rule_v2" "worker_rule_2" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_worker.id
}

resource "openstack_networking_secgroup_rule_v2" "worker_rule_3" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "udp"
  port_range_min    = 9000
  port_range_max    = 9999
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_worker.id
}

resource "openstack_networking_secgroup_rule_v2" "worker_rule_4" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "udp"
  port_range_min    = 4500
  port_range_max    = 4500
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_worker.id
}

resource "openstack_networking_secgroup_rule_v2" "worker_rule_5" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "udp"
  remote_ip_prefix  = "15.128.0.0/16"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_worker.id
}

resource "openstack_networking_secgroup_rule_v2" "worker_rule_6" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 30000
  port_range_max    = 32767
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_worker.id
}

resource "openstack_networking_secgroup_rule_v2" "worker_rule_7" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "112"
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_worker.id
}

resource "openstack_networking_secgroup_rule_v2" "worker_rule_8" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 443
  port_range_max    = 443
  remote_ip_prefix  = "0.0.0.0/0"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_worker.id
}

resource "openstack_networking_secgroup_rule_v2" "worker_rule_9" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  remote_ip_prefix  = "15.128.0.0/16"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_worker.id
}

resource "openstack_networking_secgroup_rule_v2" "worker_rule_10" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 10250
  port_range_max    = 10250
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_worker.id
}

resource "openstack_networking_secgroup_rule_v2" "worker_rule_11" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "udp"
  port_range_min    = 30000
  port_range_max    = 32767
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_worker.id
}

resource "openstack_networking_secgroup_rule_v2" "worker_rule_12" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 80
  port_range_max    = 80
  remote_ip_prefix  = "0.0.0.0/0"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_worker.id
}

resource "openstack_networking_secgroup_rule_v2" "worker_rule_13" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "udp"
  port_range_min    = 6081
  port_range_max    = 6081
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_worker.id
}

resource "openstack_networking_secgroup_rule_v2" "worker_rule_14" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "udp"
  port_range_min    = 53
  port_range_max    = 53
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_worker.id
}

resource "openstack_networking_secgroup_rule_v2" "worker_rule_15" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = "0.0.0.0/0"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_worker.id
}

resource "openstack_networking_secgroup_rule_v2" "worker_rule_16" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 1936
  port_range_max    = 1936
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_worker.id
}

resource "openstack_networking_secgroup_rule_v2" "worker_rule_17" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "icmp"
  remote_ip_prefix  = "0.0.0.0/0"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_worker.id
}

resource "openstack_networking_secgroup_rule_v2" "worker_rule_18" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "udp"
  port_range_min    = 5353
  port_range_max    = 5353
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_worker.id
}

resource "openstack_networking_secgroup_rule_v2" "worker_rule_19" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 9000
  port_range_max    = 9999
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_worker.id
}

resource "openstack_networking_secgroup_rule_v2" "worker_rule_20" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "udp"
  port_range_min    = 500
  port_range_max    = 500
  remote_ip_prefix  = "15.11.0.0/27"
  tenant_id         = openstack_identity_project_v3.%(project)s.id
  security_group_id = openstack_networking_secgroup_v2.secgroup_worker.id
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

