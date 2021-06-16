###########################################################
# 6.2. PERFORMING THE FAST FORWARD UPGRADE OF THE OVERCLOUD
###########################################################

# 0.1 Create a compute_extra.yaml template file and add this to it:
# parameter_defaults:
#  ComputeExtraConfig:
#    keystone::endpoint::admin_url: "http://1.100.1.110:35357"
#    keystone::roles::admin::password: "4gA2Ks8H7akk2NtvrADtCgfQB"

# 1. Source the stackrc file
source ~/stackrc

# 2. Run the fast forward upgrade preparation command with all relevant options and environment
#    files appropriate to your deployment:
openstack overcloud ffwd-upgrade prepare \
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

# 3. The overcloud plan updates to the OpenStack Platform 13 version. Wait until the fast forward
#    upgrade preparation completes.
# 4. Create a snapshot or backup of the overcloud before proceding with the upgrade.
# 5. Run the fast forward upgrade command
openstack overcloud ffwd-upgrade run

# 6. Wait until the fast forward upgrade completes.
