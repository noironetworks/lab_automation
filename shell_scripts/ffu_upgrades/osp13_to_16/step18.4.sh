############################################################################
# 18.4 Upgrading Compute nodes
############################################################################
# 1. Source the stackrc file:
source ~/stackrc
# 2. Migrate your instances. 
# 3. Run the upgrade command with the system_upgrade tag:
openstack overcloud upgrade run --stack overcloud --tags system_upgrade --limit overcloud-compute-0
# 4. Run the upgrade command with no tags:
openstack overcloud upgrade run --stack overcloud --limit overcloud-compute-0
# 5. To upgrade multiple Compute nodes in parallel, set the --limit option to a comma-separated list of nodes that you want to upgrade. First perform the system_upgrade task:
openstack overcloud upgrade run --stack overcloud --tags system_upgrade --limit overcloud-compute-0,overcloud-compute-1,overcloud-compute-2
# Then perform the standard OpenStack service upgrade:
openstack overcloud upgrade run --stack overcloud  --limit overcloud-compute-0,overcloud-compute-1,overcloud-compute-2
