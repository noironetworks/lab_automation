###########################################################
# 6.5. UPGRADING ALL COMPUTE NODES
###########################################################
# 1. . Source the stackrc file:
source ~/stackrc
# 2. Run the upgrade command:
openstack overcloud upgrade run --nodes Compute --skip-tags validation
# 3. Wait until the Compute node upgrade completes.
