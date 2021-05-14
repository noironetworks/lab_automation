############################################################################
# 8.4 Using predictable NIC names for overcloud nodes
############################################################################
# 1. Log in to the undercloud as the stack user.
# 2. Run the playbook-nics.yaml playbook on all overcloud nodes:
ansible-playbook -i ~/inventory.yaml playbook-nics.yaml
# The playbook sets the new NIC prefix to em. To set a different NIC prefix, set the prefix variable when running the playbook:
#    ansible-playbook -i ~/inventory.yaml -e prefix="mynic" playbook-nics.yaml
# 2.5 Remove the old udev rules from the overcloud nodes:
for server in $(nova list | awk -F"=" /overcloud/'{print $2}' | cut -d" " -f 1); do ssh heat-admin@$server "sudo rm -f /etc/udev/rules.d/70-persistent-net.rules"; done
# 3. Reboot overcloud nodes using the standard reboot procedures. 
