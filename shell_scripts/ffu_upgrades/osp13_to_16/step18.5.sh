############################################################################
# 18.5 Synchronizing the overcloud stack
############################################################################
# 1. Source the stackrc file:
source ~/stackrc
# 2. Edit the containers-prepare-parameter.yaml file and remove the following parameters and their values:
# ceph3_namespace
# ceph3_tag
# ceph3_image
# name_prefix_stein
# name_suffix_stein
# namespace_stein
# tag_stein
# 3. Run the upgrade finalization command:
openstack overcloud upgrade converge \
    --stack STACK NAME \
    --templates \
    -e ENVIRONMENT FILE
    ...
    -e /home/stack/templates/upgrades-environment.yaml \
    -e /home/stack/templates/rhsm.yaml \
    -e /home/stack/containers-prepare-parameter.yaml \
    -e /usr/share/openstack-tripleo-heat-templates/environments/services/neutron-ovs.yaml \
    ...
# 4. Wait until the stack synchronization completes.
