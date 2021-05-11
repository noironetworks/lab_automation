#########################################################
# 3.1. UPGRADING THE UNDERCLOUD TO OPENSTACK PLATFORM 11
#########################################################

# 1. Log in to director as the stack user
# 2. Disable the current OpenStack Platform repository
sudo subscription-manager repos --disable=rhel-7-server-openstack-10-rpms
# 3. Enable the new OpenStack Platform repository:
sudo subscription-manager repos --enable=rhel-7-server-openstack-11-rpms
# 4. Disable updates to the overcloud base images
sudo yum-config-manager --setopt=exclude=rhosp-director-images* --save
# 5. Stop the main OpenStack Platform services
sudo systemctl stop 'openstack-*' 'neutron-*' httpd
# 6. The default Provisioning/Control Plane network has changed from 192.0.2.0/24 to
#    192.168.24.0/24. If you used default network values in your previous undercloud.conf file, your
#    Provisioning/Control Plane network is set to 192.0.2.0/24. This means you need to set certain
#    parameters in your undercloud.conf file to continue using the 192.0.2.0/24 network.
#    Specifically, the following names are changed:
#        discovery_iprange => inspection_iprange
#        undercloud_public_vip => undercloud_public_host
#        undercloud_admin_vip => undercloud_admin_host
# 7. Run yum to upgrade the director’s main packages
sudo yum update -y instack-undercloud openstack-puppet-modules openstack-tripleocommon python-tripleoclient
# 8. Run the following command to upgrade the undercloud:
openstack undercloud upgrade
# 9. Wait until the undercloud upgrade process completes

