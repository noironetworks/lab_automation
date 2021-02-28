# DEFAULT template variables:
#    cwd: directory that tempest is run from
#
DEFAULT_TEMPLATE="""
[DEFAULT]
#debug = True
#verbose = True
log_file = %(cwd)s/tempest.log
log_dir = %(cwd)s/logs
"""

ALARMING_TEMPLATE="""
[alarming]
"""

AUTH_TEMPLATE="""
[auth]
# un-comment for juju queens
#admin_domain_name = admin_domain
"""

BAREMETAL_TEMPLATE="""
[baremetal]
"""

# Compute template variables:
#    image_uuid: uuid of image to use
#
COMPUTE_TEMPLATE="""
[compute]
image_ref = %(image_uuid)s
image_ref_alt = %(alt_image_uuid)s
flavor_ref = %(flavor_uuid)s
flavor_ref_alt = %(alt_flavor_uuid)s
image_alt_ssh_user = cirros
build_interval = 10
build_timeout = 300
ssh_connect_method = floating
ssh_user = cirros
ping_timeout = 120
ping_size = 56
use_floatingip_for_ssh = true

ssh_timeout = 300
ssh_channel_timeout = 60
ip_version_for_ssh = 4
network_for_ssh = sauto_l3out-2
"""

COMPUTE_FEATURES_TEMPLATE="""
[compute-feature-enabled]
ec2_api = false
pause = true
disk_config = false
shelve = false
suspend = true

rescue = false
preserve_ports = true
live_migration = true
enable_instance_password = true

snapshot = false
"""

# Dashboard template variables:
#    controller_ip: IP address of openstack controller
#
DASHBOARD_TEMPLATE="""
[dashboard]
dashboard_url = http://%(controller_ip)s
login_url = http://%(controller_ip)s/auth/login/
"""

DATA_PROCESSING_TEMPLATE="""
[data-processing]
"""

DATA_PROCESSING_FEATURES_TEMPLATE="""
[data-processing-feature-enabled]
"""

DATABASE_TEMPLATE="""
[database]
"""

DEBUG_TEMPLATE="""
[debug]
"""


# Identity template variables:
#    controller_ip: IP address of openstack controller
#    controller_password: admin password for controller
#
IDENTITY_TEMPLATE="""
[identity]
# un-comment for juju queens
#admin_domain_scope = True
uri = http://%(controller_ip)s:5000/v2.0/
uri_v3 = http://%(controller_ip)s:5000/v3/
#auth_version = v3
auth_version = v2
username = demo
alt_username = alt-demo
tenant_name = demo
password = %(controller_password)s
admin_role = admin
alt_tenant_name = alt-demo
admin_tenant_name = admin
admin_username = admin
alt_password = %(controller_password)s
admin_password = %(controller_password)s
# Domain name for authentication (Keystone V3).The same domain
# applies to user and project.
domain_name=Default

# Role required to administrate keystone.
admin_role=admin

# Administrative Username to use for Keystone API requests.
admin_username=admin

# API key to use when authenticating as admin.
admin_password=%(controller_password)s

# Admin domain name for authentication (Keystone V3).The same
# domain applies to user and project.
admin_domain_name=Default

# The endpoint type to use for the identity service.
endpoint_type=publicURL
#endpoint_type=v3password

# Catalog type of the Identity service.
catalog_type=identity
"""

IDENTITY_FEATURES_TEMPLATE="""
[identity-feature-enabled]
#api_v3 = true
api_v3 = false
"""

IMAGE_TEMPLATE="""
[image]
build_timeout = 300
build_interval = 1
"""

IMAGE_FEATURES_TEMPLATE="""
[image-feature-enabled]
api_v1 = false
api_v2 = true
"""

INPUT_SCENARIO_TEMPLATE="""
[input-scenario]
"""

NEGATIVE_TEMPLATE="""
[negative]
"""

# Network template variables:
#    external_network: UUID of the external network
NETWORK_TEMPLATE="""
[network]
floating_network_name = sauto_l3out-2
project_network_cidr = 192.168.0.0/16
project_network_mask_bits = 24
build_timeout = 300
build_interval = 1
public_network_id = %(external_network)s
"""

NETWORK_FEATURES_TEMPLATE="""
[network-feature-enabled]
api_extensions = default-subnetpools, network-ip-availability, network_availability_zone, auto-allocated-topology, ext-gw-mode, binding, agent, subnet_allocation, dhcp_agent_scheduler, tag, external-net, net-mtu, availability_zone, quotas, provider, multi-provider, address-scope, extraroute, servicechain, subnet-service-types, cisco-apic, standard-attr-timestamp, service-type, implicit-subnetpools, proxy_group, cisco_apic_gbp_allowed_vm_name, router, extra_dhcp_opt, standard-attr-revisions, dns-integration, pagination, sorting, cisco-apic-gbp, security-group, cisco-apic-l3, group-policy-mapping, cisco_apic_gbp_label_segmentation, rbac-policies, standard-attr-description, group-policy, port-security, allowed-address-pairs, project-id
ipv6 = false
#ipv6_subnet_attributes = true
"""

OBJECT_STORAGE_TEMPLATE="""
[object-storage]
"""

OBJECT_STORAGE_FEATURES_TEMPLATE="""
[object-storage-feature-enabled]
"""

ORCHESTRATION_TEMPLATE="""
[orchestration]
"""

OSLO_CONCURRENCY_TEMPLATE="""
[oslo_concurrency]
lock_path = %(cwd)s/tempest_lock
"""

SCENARIO_TEMPLATE="""
[scenario]
"""

SERVICE_AVAILABLE_TEMPLATE="""
[service_available]
cinder = false
ceilometer = false
swift = false
neutron = true
"""

STRESS_TEMPLATE="""
[stress]
"""

TELEMETRY_TEMPLATE="""
[telemetry]
"""

TELEMETRY_FEATURES_TEMPLATE="""
[telemetry-feature-enabled]
"""

VALIDATION_TEMPLATE="""
[validation]
ping_count = 1
connect_method = floating
auth_method = keypair
ip_version_for_ssh = 4
ping_timeout = 120
connect_timeout = 60
ssh_timeout = 300
image_ssh_user = cirros
image_ssh_password = cubswin:)
"""

VOLUME_TEMPLATE="""
[volume]
"""

VOLUME_FEATURES_TEMPLATE="""
[volume-feature-enabled]
"""

ALL_TEMPLATES = [DEFAULT_TEMPLATE, 
                 ALARMING_TEMPLATE,
                 AUTH_TEMPLATE,
                 BAREMETAL_TEMPLATE,
                 COMPUTE_TEMPLATE,
                 COMPUTE_FEATURES_TEMPLATE,
                 DASHBOARD_TEMPLATE,
                 DATA_PROCESSING_TEMPLATE,
                 DATA_PROCESSING_FEATURES_TEMPLATE,
                 DATABASE_TEMPLATE,
                 DEBUG_TEMPLATE,
                 IDENTITY_TEMPLATE,
                 IDENTITY_FEATURES_TEMPLATE,
                 IMAGE_TEMPLATE,
                 IMAGE_FEATURES_TEMPLATE,
                 INPUT_SCENARIO_TEMPLATE,
                 NEGATIVE_TEMPLATE,
                 NETWORK_TEMPLATE,
                 NETWORK_FEATURES_TEMPLATE,
                 OBJECT_STORAGE_TEMPLATE,
                 OBJECT_STORAGE_FEATURES_TEMPLATE,
                 ORCHESTRATION_TEMPLATE,
                 OSLO_CONCURRENCY_TEMPLATE,
                 SCENARIO_TEMPLATE,
                 SERVICE_AVAILABLE_TEMPLATE,
                 STRESS_TEMPLATE,
                 TELEMETRY_TEMPLATE,
                 TELEMETRY_FEATURES_TEMPLATE,
                 VALIDATION_TEMPLATE,
                 VOLUME_TEMPLATE,
                 VOLUME_FEATURES_TEMPLATE
                ]
