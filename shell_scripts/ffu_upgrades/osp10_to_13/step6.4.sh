###########################################################
# 6.4. UPGRADING TEST COMPUTE NODES
###########################################################
# 1. . Source the stackrc file:
source ~/stackrc
# 2. Run the upgrade command:
# openstack overcloud upgrade run --nodes compute-0 --skip-tags validation
# 3. Wait until the test node upgrade completes.
