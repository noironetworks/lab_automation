############################################################################
# 6.11 Running the director upgrade
############################################################################
# 0. Remove /etc/os-net-config/config.json
sudo rm -f /etc/os-net-config/config.json
# 0.2 Save off old network interface
sudo mv /etc/sysconfig/network-scripts/ifcfg-ens192 /etc/sysconfig/network-scripts/ifcfg-ens192.bak
# 1. Run the following command to upgrade the director on the undercloud:
openstack undercloud upgrade
# 2. The script also starts all OpenStack Platform service containers on the undercloud automatically. You manage each service through a systemd resource. Check the systemd resources:
sudo systemctl list-units "tripleo_*"
# 2.1 Each systemd service controls a container. Check the enabled containers using the following command:
sudo podman ps
# 3. The script adds the stack user to the docker group to ensure that the stack user has access to container management commands. Refresh the stack user permissions with the following command:
exec su -l stack
# 3.1 The command prompts you to log in again. Enter the stack user password.
# 4. To initialize the stack user to use the command line tools, run the following command:
source ~/stackrc
