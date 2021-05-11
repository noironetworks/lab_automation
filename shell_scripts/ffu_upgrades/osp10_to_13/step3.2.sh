#########################################################
# 3.2. UPGRADING THE UNDERCLOUD TO OPENSTACK PLATFORM 12
#########################################################

# 1. Log in to director as the stack user
# 2. Disable the current OpenStack Platform repository
sudo subscription-manager repos --disable=rhel-7-server-openstack-11-rpms
# 3. Enable the new OpenStack Platform repository
sudo subscription-manager repos --enable=rhel-7-server-openstack-12-rpms
# 4. Disable updates to the overcloud base images
sudo yum-config-manager --setopt=exclude=rhosp-director-images* --save
# 5. Run yum to upgrade the director’s main packages
sudo yum update -y python-tripleoclient
# 6. Edit the /home/stack/undercloud.conf file and check that the enabled_drivers parameter
#    does not contain the pxe_ssh drive
# 7. Run the following command to upgrade the undercloud:
openstack undercloud upgrade
# 8. Wait until the undercloud upgrade process completes
