############################################################################
# 7.5 Creating an overcloud inventory file
############################################################################
# 1. Log in to the undercloud as the stack user.
# 2. Source the stackrc file.
source ~/stackrc
# 3. Create a static inventory file of all nodes:
tripleo-ansible-inventory --static-yaml-inventory ~/inventory.yaml --stack STACK_NAME
# 4 To execute Ansible playbooks on your environment, run the ansible-playbook command and include the full path of the dynamic inventory tool using the -i option. For example:
ansible-playbook -i ~/inventory.yaml PLAYBOOK
