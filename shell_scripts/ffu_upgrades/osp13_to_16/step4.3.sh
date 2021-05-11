############################################################################
# 4.3. Using predictable NIC names for the undercloud node
############################################################################
# 1. Log in to the undercloud as the stack user.
# 2. Create an Ansible playbook named playbook-nics.yaml and copy the following content into the playbook:
cat > playbook-nics.yaml << EOL
---
- name: Rename eth devices
  hosts: all
  become: yes
  vars:
    prefix: "em"
  tasks:
    - set_fact:
        eth_interfaces: "{{ ansible_interfaces | select('match','eth.*') | list }}"
    - debug:
        msg: "{{ eth_interfaces }}"
    - name: Update udev rules
      lineinfile:
        line: "SUBSYSTEM==\"net\", ACTION==\"add\", DRIVERS==\"?*\", ATTR{address}==\"{{ ansible_facts[item]['perm_macaddress'] | default(ansible_facts[item]['macaddress']) }}\", NAME=\"{{ item|replace('eth',prefix) }}\""
        path: /etc/udev/rules.d/70-rhosp-persistent-net.rules
        create: True
      with_items: "{{ eth_interfaces }}"
    - name: Rename eth files
      block:
        - name: Check that eth files exists
          stat:
            path: /etc/sysconfig/network-scripts/ifcfg-{{ item }}
          register: nic_result
          with_items: "{{ eth_interfaces }}"
        - name: Copy nic files using the new prefix
          copy:
            remote_src: True
            src: "{{ item.stat.path }}"
            dest: "{{ item.stat.path|replace('eth',prefix) }}"
          with_items: "{{ nic_result.results }}"
          when: item.stat.exists
        - name: Edit NAME in new network-script files
          lineinfile:
            regexp: "^NAME=.*"
            line: "NAME={{ item.item|replace('eth',prefix) }}"
            path: "{{ item.stat.path|replace('eth',prefix) }}"
          with_items: "{{ nic_result.results }}"
          when: item.stat.exists
        - name: Edit DEVICE in new network-script files
          lineinfile:
            regexp: "^DEVICE=.*"
            line: "DEVICE={{ item.item|replace('eth',prefix) }}"
            path: "{{ item.stat.path|replace('eth',prefix) }}"
          with_items: "{{ nic_result.results }}"
          when: item.stat.exists
        - name: Backup old eth network-script files
          copy:
            remote_src: True
            src: "{{ item.stat.path }}"
            dest: "{{ item.stat.path }}.bak"
          with_items: "{{ nic_result.results }}"
          when: item.stat.exists
        - name: Remove old eth network-script files
          file:
            path: "{{ item.stat.path }}"
            state: absent
          with_items: "{{ nic_result.results }}"
          when: item.stat.exists
    - name: Rename route files
      block:
        - name: Check that route files exists
          stat:
            path: /etc/sysconfig/network-scripts/route-{{ item }}
          register: route_result
          with_items: "{{ eth_interfaces }}"
        - name: Copy route files using the new prefix
          copy:
            remote_src: True
            src: "{{ item.stat.path }}"
            dest: "{{ item.stat.path|replace('eth',prefix) }}"
          with_items: "{{ route_result.results }}"
          when: item.stat.exists
        - name: Update prefix in route files that use IP command arguments format
          replace:
            regexp: "eth"
            replace: "{{ prefix }}"
            path: "{{ item.stat.path|replace('eth',prefix) }}"
          with_items: "{{ route_result.results }}"
          when: item.stat.exists
        - name: Backup old route files
          copy:
            remote_src: True
            src: "{{ item.stat.path }}"
            dest: "{{ item.stat.path }}.bak"
          with_items: "{{ route_result.results }}"
          when: item.stat.exists
        - name: Remove old route files
          file:
            path: "{{ item.stat.path }}"
            state: absent
          with_items: "{{ route_result.results }}"
          when: item.stat.exists
    - name: Perform a final regex for any remaining eth prefixes in ifcfg files
      block:
        - name: Get a list of all ifcfg files
          find:
            paths: /etc/sysconfig/network-scripts/
            patterns: 'ifcfg-*'
          register: ifcfg_files
        - name: Perform final regex on ifcfg files
          replace:
            path: "{{ item[0].path }}"
            regexp: "{{ item[1] }}"
            replace: "{{ item[1]|replace('eth',prefix) }}"
          with_nested:
            - "{{ ifcfg_files.files }}"
            - "{{ eth_interfaces }}"
EOL
# 3. Run the playbook-nics.yaml playbook on the undercloud:
# The playbook sets the new NIC prefix to em. To set a different NIC prefix, set the prefix variable when running the playbook:
#   ansible-playbook -c local -i localhost, -e prefix="mynic" ~/playbook-nics.yaml
ansible-playbook -c local -i localhost, playbook-nics.yaml
# 3.5 Remove the udev rules for the old interfaces.
sudo rm -f /etc/udev/rules.d/70-persistent-net.rules
# 4. Reboot the undercloud node using the standard reboot procedures.
sudo reboot
