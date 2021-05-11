###########################################################
# 6.3. UPGRADING CONTROLLER AND CUSTOM ROLE NODES
###########################################################
# 1. . Source the stackrc file:
source ~/stackrc
# 2. If you use monolithic Controller nodes, run the upgrade command against the Controller role:
openstack overcloud upgrade run --nodes Controller --skip-tags validation
# 3. If you use Controller services split across multiple roles:
# 3a. Run the upgrade command for roles with Pacemaker services:
#     openstack overcloud upgrade run --nodes ControllerOpenStack --skip-tags validation
#     openstack overcloud upgrade run --nodes Database --skip-tags validation
#     openstack overcloud upgrade run --nodes Messaging --skip-tags validation
#     openstack overcloud upgrade run --nodes Telemetry --skip-tags validation
# 3b. Run the upgrade command for the Networker role:
#     openstack overcloud upgrade run --nodes Networker --skip-tags validation
# 3c. Run the upgrade command for any remaining custom roles, except for Compute or
#     CephStorage roles:
#     openstack overcloud upgrade run --nodes ObjectStorage --skip-tags validation

