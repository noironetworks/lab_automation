################################
# 2.9. REBOOTING COMPUTE NODES
################################

# 1. Log in to the undercloud as the stack user
# 2. To identify the UUID of the Compute node you aim to reboot, list all Compute nodes
source ~/stackrc
openstack server list --name compute
# 3. From the overcloud, select a Compute Node and disable it
source ~/overcloudrc
openstack compute service list
openstack compute service set <hostname> nova-compute --disable
# 4. List all instances on the Compute node
openstack server list --host <hostname> --all-projects
# 5. Migrate your instances
# 6. Log into the Compute Node and reboot it
sudo reboot
# 7. Wait until the node boots
# 8. Enable the Compute node
source ~/overcloudrc
openstack compute service set <hostname> nova-compute --enable
# 9. Verify that the Compute node is enabled
openstack compute service list
