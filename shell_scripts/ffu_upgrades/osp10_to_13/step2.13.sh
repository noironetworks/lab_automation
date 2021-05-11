########################################################
# 2.13. FINALIZING UPDATES FOR NFV-ENABLED ENVIRONMENTS
########################################################

# 1. Find the server ID for the instance you want to take a snapshot of
openstack server list
# 2. Shut down the source instance before you take the snapshot to ensure that all
#    data is flushed to disk:
openstack server stop SERVER_ID
# 3. Create the snapshot image of the instance
openstack image create --id SERVER_ID SNAPSHOT_NAME
# 4. Boot a new instance with this snapshot image
openstack server create --flavor DPDK_FLAVOR --nic net-id=DPDK_NET_ID--image SNAPSHOT_NAME INSTANCE_NAME
# 5. Optionally, verify that the new instance status is ACTIVE
openstack server list
