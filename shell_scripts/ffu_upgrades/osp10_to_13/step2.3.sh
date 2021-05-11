############################################################################
# 2.3 UPDATING THE CURRENT UNDERCLOUD PACKAGES FOR OPENSTACK PLATFORM 10.Z
############################################################################

# 1. Log in to the undercloud as the stack user
if [ "$(whoami)" != "stack" ]; then
    echo "You're not stack!"
fi
# 2. Stop the main OpenStack Platform services
sudo systemctl stop 'openstack-*' 'neutron-*' httpd
# 3. Set the RHEL version to RHEL 7.7:
sudo subscription-manager release --set=7.7
# 4. Update the python-tripleoclient package and its dependencies to ensure you have the latest scripts for the minor version update
sudo yum update -y python-tripleoclient
# 5. Run the openstack undercloud upgrade command
source ~/stackrc && openstack undercloud upgrade
# 6. Wait until the command completes its execution
# 7. Reboot the undercloud to update the operating system’s kernel and other system packages
sudo reboot
# 8. Wait until the node boots
# 9. Log into the undercloud as the stack user
