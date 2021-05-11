########################################################
# 2.11. VALIDATING AN OPENSTACK PLATFORM 10 UNDERCLOUD
########################################################

# 1. Source the undercloud access details
source ~/stackrc
# 2. Check for failed Systemd services
sudo systemctl list-units --state=failed 'openstack*' 'neutron*' 'httpd' 'docker'
# 3. Check the undercloud free space
df -h
# 4. If you have NTP installed on the undercloud, check the clock is synchronized
sudo ntpstat
# 5. Check the undercloud network services
openstack network agent list
# 6. Check the undercloud compute services
openstack compute service list

