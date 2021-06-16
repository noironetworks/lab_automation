############################################################################
# 8.3 Copying the Leapp data to the overcloud nodes
############################################################################
# 1. Log in to the undercloud as the stack user.
# 2. Source the stackrc file.
source ~/stackrc
# 3. Create a static inventory file of all the nodes in your environment:
tripleo-ansible-inventory --static-yaml-inventory ~/inventory.yaml --stack overcloud
# 4. To copy the leapp data to the overcloud nodes, run the following synchronize Ansible command:
ansible -i ~/inventory.yaml --become -m synchronize -a "src=/etc/leapp/files dest=/etc/leapp/" overcloud
