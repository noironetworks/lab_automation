############################################################################
# 8.4 Using predictable NIC names for overcloud nodes
############################################################################
# 1. Log in to the undercloud as the stack user.
# 2. Run the playbook-nics.yaml playbook on all overcloud nodes:
ansible-playbook -i ~/inventory.yaml playbook-nics.yaml
# The playbook sets the new NIC prefix to em. To set a different NIC prefix, set the prefix variable when running the playbook:
#    ansible-playbook -i ~/inventory.yaml -e prefix="mynic" playbook-nics.yaml
# 3. Reboot overcloud nodes using the standard reboot procedures. 
