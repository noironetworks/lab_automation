############################################################################
# 9.2 Updating composable services in custom environment files
############################################################################
# 1. Search for custom environment files that use composable services. You usually store custom environment files in the /home/stack/templates directory:
cd ~/templates/
grep "OS::TripleO::Services" *
# 2. Identify the new ceph-mgr.yaml location in /usr/share/openstack-tripleo-heat-templates/. This file is now located in the `deployment/ceph-ansible' directory:
find /usr/share/openstack-tripleo-heat-templates/ -name ceph-mgr.yaml
# should show: /usr/share/openstack-tripleo-heat-templates/deployment/ceph-ansible/ceph-mgr.yaml
# 3. Edit the service in the custom environment file:
# resource_registry:
#  OS::TripleO::Services::CephMgr: /usr/share/openstack-tripleo-heat-templates/deployment/ceph-ansible/ceph-mgr.yaml
# 4. Here are the changes for FAB2021:
   #controller
   OS::TripleO::ControllerExtraConfigPre: /opt/ciscoaci-tripleo-heat-templates//nodepre.yaml
   OS::TripleO::Services::NeutronL3Agent: OS::Heat::None
-  OS::TripleO::Services::NeutronOvsAgent: /opt/ciscoaci-tripleo-heat-templates/docker/services/cisco_opflex.yaml
-  OS::TripleO::Docker::NeutronMl2PluginBase: /opt/ciscoaci-tripleo-heat-templates/puppet/services/ciscoaci-ml2.yaml
-  OS::TripleO::Services::CiscoAciAIM: /opt/ciscoaci-tripleo-heat-templates/docker/services/cisco_aciaim.yaml
+  OS::TripleO::Services::NeutronOvsAgent: /opt/ciscoaci-tripleo-heat-templates/deployment/opflex/opflex-agent-container-puppet.yaml
+  OS::TripleO::Docker::NeutronMl2PluginBase: /opt/ciscoaci-tripleo-heat-templates/deployment/neutron/neutron-ml2-ciscoaci.yaml
+  OS::TripleO::Services::CiscoAciAIM: /opt/ciscoaci-tripleo-heat-templates/deployment/aciaim/cisco-aciaim-container-puppet.yaml
+  OS::TripleO::Services::NeutronMetadataAgent: /usr/share/openstack-tripleo-heat-templates/deployment/neutron/neutron-metadata-container-puppet.yaml
+  OS::TripleO::Services::NeutronDhcpAgent: /usr/share/openstack-tripleo-heat-templates/deployment/neutron/neutron-dhcp-container-puppet.yaml
   #compute
   OS::TripleO::ComputeExtraConfigPre: /opt/ciscoaci-tripleo-heat-templates//nodepre.yaml
-  OS::TripleO::Services::ComputeNeutronOvsAgent: /opt/ciscoaci-tripleo-heat-templates/docker/services/cisco_opflex.yaml
-  OS::TripleO::Services::ComputeNeutronCorePlugin: /opt/ciscoaci-tripleo-heat-templates/puppet/services/ciscoaci_compute.yaml
-  OS::TripleO::Services::ComputeNeutronMetadataAgent: /opt/ciscoaci-tripleo-heat-templates/docker/services/compute-neutron-metadata.yaml
+  OS::TripleO::Services::ComputeNeutronOvsAgent: /opt/ciscoaci-tripleo-heat-templates/deployment/opflex/opflex-agent-container-puppet.yaml
+  OS::TripleO::Services::ComputeNeutronMetadataAgent: /opt/ciscoaci-tripleo-heat-templates/deployment/compute_neutron_metadata/compute-neutron-metadata.yaml

-  OS::TripleO::Services::CiscoAciLldp: /opt/ciscoaci-tripleo-heat-templates/docker/services/cisco_lldp.yaml
+  OS::TripleO::Services::CiscoAciLldp: /opt/ciscoaci-tripleo-heat-templates/deployment/lldp/cisco_lldp.yaml

+  OS::TripleO::Services::OVNDBs: OS::Heat::None
+  OS::TripleO::Services::OVNController: OS::Heat::None
+  OS::TripleO::Services::OVNMetadataAgent: OS::Heat::None
+  OS::TripleO::Services::ComputeNeutronL3Agent: OS::Heat::None
+  OS::TripleO::Services::NeutronL3Agent: OS::Heat::None



@@ -30,7 +36,7 @@
   OvercloudComputeFlavor: compute


-  DockerInsecureRegistryAddress: 1.100.1.1:8787,10.30.120.22:8787
+  DockerInsecureRegistryAddress: ["ostack-pt-1-s1-ucloud-13.ctlplane.localdomain:8787", "1.100.1.1:8787", "10.30.120.22:8787"]


   ControllerCount: 3
@@ -77,5 +83,5 @@
   AciVmmMulticastAddress: 225.21.10.3


-  ACIYumRepo: http://1.100.1.1/acirepo
+  ACIYumRepo: http://1.100.1.1:8787/v2/__acirepo
