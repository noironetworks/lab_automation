##########################################################
# 3.3. UPGRADING THE UNDERCLOUD TO OPENSTACK PLATFORM 13
##########################################################

# 1. Log in to director as the stack user
# 2. Disable the current OpenStack Platform repository
sudo subscription-manager repos --disable=rhel-7-server-openstack-12-rpms
# 3. Set the RHEL version to RHEL 7.9
sudo subscription-manager release --set=7.9
# 4. Enable the new OpenStack Platform repository
sudo subscription-manager repos --enable=rhel-7-server-openstack-13-rpms
# 4.5 Enable extra repos (missing from original documentation)
sudo subscription-manager repos --enable=rhel-7-server-extras-rpms
sudo subscription-manager repos --enable=rhel-ha-for-rhel-7-server-rpms
# 5. Re-enable updates to the overcloud base images
sudo yum-config-manager --setopt=exclude= --save
# 6. Run yum to upgrade the director’s main packages
sudo yum update -y python-tripleoclient
# 7. Run the following command to upgrade the undercloud:
openstack undercloud upgrade
# 8. Wait until the undercloud upgrade process completes
# 9. Reboot the undercloud to update the operating system’s kernel and other system packages
sudo reboot
# 10. Wait until the node boots

