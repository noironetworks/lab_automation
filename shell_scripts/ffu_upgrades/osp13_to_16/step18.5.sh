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
# 3.1 Create upgrade_converge.sh script:
cat > upgrade_converge.sh << EOL
openstack overcloud upgrade converge \
    --templates /home/stack/tripleo-heat-templates \
    -r /home/stack/templates/aci_roles_data.yaml \
    -e /home/stack/templates/upgrades-environment.yaml \
    -e /home/stack/templates/rhsm.yaml \
    -e /home/stack/templates/containers-prepare-parameter.yaml \
    -e /home/stack/tripleo-heat-templates/environments/network-isolation.yaml \
    -e /home/stack/templates/network-environment.yaml \
    -e /home/stack/templates/ciscoaci_containers.yaml \
    -e /home/stack/templates/ciscoaci_containers_stein.yaml \
    -e /home/stack/templates/ciscoaci-config.yaml
EOL
# 2.1 Make it executable:
chmod +x ./upgrade_converge.sh
# 2.2 Run the upgrade converge:
./upgrade_converge.sh
# 4. Wait until the stack synchronization completes.
