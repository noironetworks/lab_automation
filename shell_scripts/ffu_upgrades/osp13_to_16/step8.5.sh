############################################################################
# 8.5 Setting the SSH root permission parameter on the overcloud
############################################################################
# 1. Log in to the undercloud as the stack user.
# 2. Create a file called playbook-ssh.yaml and paste the following content in the file:
cat > playbook-ssh.yaml << EOL
---
- name: Configure SSH PermitRootLogin parameter
  hosts: overcloud
  become: yes
  tasks:
    - name: Set the PermitRootLogin parameter to no
      lineinfile:
        path: /etc/ssh/sshd_config
        state: present
        line: "PermitRootLogin no"
EOL
# 3. Run the playbook:
ansible-playbook -i ~/inventory.yaml playbook-ssh.yaml
# 4. Run the playbook to clean up the repos:
cat > playbook_rmrepo.yaml << EOL
---
- name: Remove ACI Repo
  hosts: overcloud
  become: yes
  tasks:
    - name: remove_acirepo
      ansible.builtin.file:
        path: /etc/yum.repos.d/ciscoaci.repo
        state: absent
EOL
sudo mv playbook_rmrepo.yaml /opt/ciscoaci-tripleo-heat-templates/tools/playbook_rmrepo.yaml
ansible-playbook -i ~/inventory.yaml /opt/ciscoaci-tripleo-heat-templates/tools/playbook_rmrepo.yaml
