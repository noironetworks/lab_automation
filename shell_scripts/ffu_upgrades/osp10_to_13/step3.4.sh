########################################################
# 3.4. DISABLING DEPRECATED SERVICES ON THE UNDERCLOUD
########################################################

# 1. Log in to the undercloud as the stack user
# 2. Stop and disable the openstack-glance-registry service
sudo systemctl stop openstack-glance-registry
sudo systemctl disable openstack-glance-registry
# 3. Stop and disable the mongod service
sudo systemctl stop mongod
sudo systemctl disable mongod
