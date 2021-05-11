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
