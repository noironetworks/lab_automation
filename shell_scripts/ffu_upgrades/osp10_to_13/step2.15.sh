##########################
# 2.15 ACI SPECIFIC STEPS
##########################

# 1. Remove tripleo-ciscoaci package at this time
sudo rpm -ev tripleo-ciscoaci
sudo rm -rf /var/www/html/acirepo
# 2. Install the tripleo-ciscoaci package for ocata
sudo rpm -ihv tripleo-ciscoaci-11.0-750.noarch.rpm
# 3. Copy the ocata repo to its own directory
sudo mv /var/www/html/acirepo /var/www/html/acirepo11
sudo mv openstack-neutron-gbp-6.10.12-220.el7.noarch.rpm /var/www/html/acirepo11
sudo createrepo /var/www/html/acirepo11
# 4. Remove the tripleo-ciscoaci package
sudo rpm -ev tripleo-ciscoaci
# 5. Install the tripleo-ciscoaci package for pike
sudo rpm -ihv tripleo-ciscoaci-12.0-749.noarch.rpm
# 6. Copy the pike repo to its own directory
sudo mv /var/www/html/acirepo /var/www/html/acirepo12
sudo mv openstack-neutron-gbp-7.4.13-158.el7.noarch.rpm /var/www/html/acirepo12
sudo createrepo /var/www/html/acirepo12
# 7. Remove the tripleo-ciscoaci package
sudo rpm -ev tripleo-ciscoaci
# 8. Install the tripleo-ciscoaci package for queens
sudo rpm -ihv tripleo-ciscoaci-13.0-1027.noarch.rpm
# 9. Copy the queens repo to its own directory (no longer needed)
#sudo cp -r /var/www/html/acirepo /var/www/html/acirepo13
# 9. Edit the tripleo script to remove references to plugin.ini:
vi /opt/ciscoaci-tripleo-heat-templates/docker/services/cisco_aciaim.yaml
