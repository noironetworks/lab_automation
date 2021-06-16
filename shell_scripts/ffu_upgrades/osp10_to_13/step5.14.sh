--- templates/ciscoaci-config.yaml	2021-03-16 17:33:03.863616973 -0700
+++ ciscoaci-config.yaml	2021-03-17 06:55:35.727019965 -0700
@@ -3,25 +3,64 @@
 resource_registry:

   #controller
-  OS::TripleO::ControllerExtraConfigPre: /opt/tripleo-ciscoaci/nodepre.yaml
+  OS::TripleO::ControllerExtraConfigPre: /opt/ciscoaci-tripleo-heat-templates//nodepre.yaml
   OS::TripleO::Services::NeutronL3Agent: OS::Heat::None
-  OS::TripleO::Services::NeutronOvsAgent: OS::Heat::None
-  OS::TripleO::Services::NeutronCorePlugin: OS::TripleO::Services::NeutronCorePluginCiscoAci
-  OS::TripleO::Services::NeutronCorePluginCiscoAci: /opt/tripleo-ciscoaci/ciscoaci.yaml
-  OS::TripleO::Services::HorizonCiscoAci: /opt/tripleo-ciscoaci/ciscoaci_horizon.yaml
-  OS::TripleO::Services::HeatCiscoAci: /opt/tripleo-ciscoaci/ciscoaci_heat.yaml
+  OS::TripleO::Services::NeutronOvsAgent: /opt/ciscoaci-tripleo-heat-templates/docker/services/cisco_neutron_opflex.yaml
+  OS::TripleO::Docker::NeutronMl2PluginBase: /opt/ciscoaci-tripleo-heat-templates/puppet/services/ciscoaci-ml2.yaml
+  OS::TripleO::Services::CiscoAciAIM: /opt/ciscoaci-tripleo-heat-templates/docker/services/cisco_aciaim.yaml
+  OS::TripleO::Services::CiscoAciOpflexAgent: /opt/ciscoaci-tripleo-heat-templates/docker/services/cisco_opflex.yaml
   #OS::TripleO::Services::NeutronSriovAgent: /usr/share/openstack-tripleo-heat-templates/puppet/services/neutron-sriov-agent.yaml
   #compute
-  OS::TripleO::ComputeExtraConfigPre: /opt/tripleo-ciscoaci/nodepre.yaml
-  OS::TripleO::Services::ComputeNeutronOvsAgent: OS::Heat::None
-  OS::TripleO::Services::ComputeNeutronCorePlugin: /opt/tripleo-ciscoaci/ciscoaci_compute.yaml
-  OS::TripleO::Services::ComputeNeutronMetadataAgent: /usr/share/openstack-tripleo-heat-templates/puppet/services/neutron-metadata.yaml
+  OS::TripleO::ComputeExtraConfigPre: /opt/ciscoaci-tripleo-heat-templates//nodepre.yaml
+  OS::TripleO::Services::ComputeNeutronOvsAgent: /opt/ciscoaci-tripleo-heat-templates/docker/services/cisco_neutron_opflex.yaml
+  OS::TripleO::Services::ComputeNeutronCorePlugin: /opt/ciscoaci-tripleo-heat-templates/puppet/services/ciscoaci_compute.yaml
+  OS::TripleO::Services::ComputeNeutronMetadataAgent: /opt/ciscoaci-tripleo-heat-templates/docker/services/compute-neutron-metadata.yaml
+  OS::TripleO::Services::ComputeCiscoAciOpflexAgent: /opt/ciscoaci-tripleo-heat-templates/docker/services/cisco_opflex.yaml
+  OS::TripleO::Services::CiscoAciLldp: /opt/ciscoaci-tripleo-heat-templates/docker/services/cisco_lldp.yaml





 parameter_defaults:
+  FastForwardCustomRepoScriptContent: |
+      #!/bin/bash
+      set -e
+      echo "If you use FastForwardRepoType 'custom-script' you have to provide the upgrade repo script content."
+      echo "It will be installed as /root/ffu_upgrade_repo.sh on the node"
+      echo "and passed the upstream name (ocata, pike, queens) of the release as first argument"
+      case $1 in
+        ocata)
+          subscription-manager repos --disable=rhel-7-server-openstack-10-rpms
+          subscription-manager repos --enable=rhel-7-server-openstack-11-rpms
+          yum-config-manager --disable acirepo10
+          yum-config-manager --enable acirepo11
+          ;;
+        pike)
+          subscription-manager repos --disable=rhel-7-server-openstack-11-rpms
+          subscription-manager repos --enable=rhel-7-server-openstack-12-rpms
+          yum-config-manager --disable acirepo11
+          yum-config-manager --enable acirepo12
+          ;;
+        queens)
+          subscription-manager repos --disable=rhel-7-server-openstack-12-rpms
+          subscription-manager release --set=7.9
+          subscription-manager repos --enable=rhel-7-server-openstack-13-rpms
+          subscription-manager repos --disable=rhel-7-server-rhceph-2-osd-rpms || true
+          subscription-manager repos --disable=rhel-7-server-rhceph-2-mon-rpms
+          subscription-manager repos --enable=rhel-7-server-rhceph-3-mon-rpms
+          subscription-manager repos --disable=rhel-7-server-rhceph-2-tools-rpms
+          subscription-manager repos --enable=rhel-7-server-rhceph-3-tools-rpms
+          yum-config-manager --disable acirepo12
+          yum-config-manager --enable acirepo
+          ;;
+        *)
+          echo "unknown release $1" >&2
+          exit 1
+      esac
+  EC2MetadataIp: 1.100.1.1
+  ControlPlaneDefaultRoute: 1.100.1.1
+  OvercloudControllerFlavor: control
+  OvercloudComputeFlavor: compute
+
+
+  DockerInsecureRegistryAddress: 1.100.1.1:8787,10.30.120.22:8787

   ControllerCount: 1
   ComputeCount: 2
