############################################################################
# 5.3  NEW COMPOSABLE SERVICES
############################################################################
# 1. copy /usr/share/openstack-tripleo-heat-templates/roles_data.yaml to 
#    /home/stack/templates/custom_roles_data.yaml
cp /usr/share/openstack-tripleo-heat-templates/roles_data.yaml /home/stack/templates/custom_roles_data.yaml
# 2. Add the new composable services. For controller:
+    - OS::TripleO::Services::CiscoAciAIM
+    - OS::TripleO::Services::CiscoAciLldp
+    - OS::TripleO::Services::CiscoAciOpflexAgent
#    For compute:
+    - OS::TripleO::Services::CiscoAciLldp
+    - OS::TripleO::Services::ComputeCiscoAciOpflexAgent

