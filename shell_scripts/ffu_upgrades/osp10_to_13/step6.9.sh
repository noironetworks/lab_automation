###########################################################
# 6.9. FINALIZING THE FAST FORWARD UPGRADE
###########################################################
# 1. . Source the stackrc file:
source ~/stackrc
# 2. Run the fast forward upgrade finalization command:
openstack overcloud ffwd-upgrade converge \
    --templates \
    -r /home/stack/templates/custom_roles_data.yaml \
    -e /home/stack/templates/overcloud_images.yaml \
    -e /home/stack/templates/ciscoaci_containers.yaml \
    -e /usr/share/openstack-tripleo-heat-templates/environments/network-isolation.yaml \
    -e /home/stack/templates/network-environment.yaml \
    -e /home/stack/templates/ciscoaci-config.yaml \
    -e /home/stack/templates/compute_extra.yaml \
    -e /home/stack/templates/sauto.yaml \
    --ntp-server 172.28.184.8 \
    --control-flavor control \
    --compute-flavor compute
# 3. Wait until the fast forward upgrade finalization completes.
