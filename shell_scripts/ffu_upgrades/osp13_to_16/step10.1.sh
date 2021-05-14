############################################################################
# 10.1 Red Hat Subscription Manager (RHSM) composable service
############################################################################
# 1. To enable the service, register the resource to the rhsm composable service file:
# resource_registry:
#   OS::TripleO::Services::Rhsm: /usr/share/openstack-tripleo-heat-templates/deployment/rhsm/rhsm-baremetal-ansible.yaml
# 1.1 Edit the templates/ciscoaci-config.yaml file and add this:
#   OS::TripleO::Services::Rhsm: /usr/share/openstack-tripleo-heat-templates/deployment/rhsm/rhsm-baremetal-ansible.yaml
# 2. The rhsm composable service accepts a RhsmVars parameter, which you can use to define multiple sub-parameters relevant to your registration:
cat > /home/stack/templates/rhsm.yaml << EOL
resource_registry:
  OS::TripleO::Services::Rhsm: /usr/share/openstack-tripleo-heat-templates/deployment/rhsm/rhsm-baremetal-ansible.yaml
parameter_defaults:
  RhsmVars:
    rhsm_repos:
        - rhel-8-for-x86_64-baseos-eus-rpms
        - rhel-8-for-x86_64-appstream-eus-rpms
        - rhel-8-for-x86_64-highavailability-eus-rpms
        - ansible-2.9-for-rhel-8-x86_64-rpms
        - advanced-virt-for-rhel-8-x86_64-rpms
        - openstack-16.1-for-rhel-8-x86_64-rpms
        - rhceph-4-mon-for-rhel-8-x86_64-rpms
        - rhceph-4-tools-for-rhel-8-x86_64-rpms
        - fast-datapath-for-rhel-8-x86_64-rpms
    rhsm_username: "mcohen2@cisco.com"
    rhsm_password: "Ins3965!"
    rhsm_org_id: "7436133"
    rhsm_pool_ids: "8a85f99a766234dd0176905c321f0c1f"
    rhsm_method: "portal"
    rhsm_rhsm_proxy_hostname: "proxy.esl.cisco.com"
    rhsm_rhsm_proxy_port: "80"
    rhsm_release: 8.2
EOL

# 3. You can also use the RhsmVars parameter in combination with role-specific parameters, for example, ControllerParameters, to provide flexibility when enabling specific repositories for different nodes types
