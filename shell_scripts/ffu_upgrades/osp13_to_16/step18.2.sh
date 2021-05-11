############################################################################
# 18.2 Upgrading Controller nodes with director-deployed Ceph Storage
############################################################################
# 1. Source the stackrc file:
source ~/stackrc
# 2. Identify the bootstrap Controller node by running the following command on a Controller node:
sudo hiera -c /etc/puppet/hiera.yaml pacemaker_short_bootstrap_node_name
# To run this command from the undercloud, run the following SSH command and substitute CONTROLLER_IP with the IP address of any Controller node in your environment:
# ssh heat-admin@CONTROLLER_IP "sudo hiera -c /etc/puppet/hiera.yaml pacemaker_short_bootstrap_node_name"
# 3. Upgrade the bootstrap Controller node:
# 3.1 Run the external upgrade command with the ceph_systemd tag:
openstack overcloud external-upgrade run --stack overcloud --tags ceph_systemd -e ceph_ansible_limit=overcloud-controller-0
# 3.2 Run the upgrade command with the system_upgrade tag:
openstack overcloud upgrade run --stack overcloud --tags system_upgrade --limit overcloud-controller-0
# 3.3 Run the external upgrade command with the system_upgrade_transfer_data tag:
openstack overcloud external-upgrade run --stack overcloud --tags system_upgrade_transfer_data
# 3.4 Run the upgrade command with the nova_hybrid_state tag and run only the upgrade_steps_playbook.yaml playbook:
openstack overcloud upgrade run --stack overcloud --playbook upgrade_steps_playbook.yaml --tags nova_hybrid_state --limit all
# 3.5 Run the upgrade command with no tags:
openstack overcloud upgrade run --stack overcloud --limit overcloud-controller-0
# 4. Upgrade the next Controller node:
# 4.1 Run the external upgrade command with the ceph_systemd tag:
openstack overcloud external-upgrade run --stack overcloud --tags ceph_systemd -e ceph_ansible_limit=overcloud-controller-1
# 4.2 Run the upgrade command with the system_upgrade tag on the next Controller node:
openstack overcloud upgrade run --stack overcloud --tags system_upgrade --limit overcloud-controller-1
# 4.3 Run the upgrade command with no tags:
openstack overcloud upgrade run --stack overcloud --limit overcloud-controller-0,overcloud-controller-1
# 5. Upgrade the final Controller node:
# 5.1 Run the external upgrade command with the ceph_systemd tag:
openstack overcloud external-upgrade run --stack overcloud --tags ceph_systemd -e ceph_ansible_limit=overcloud-controller-2
# 5.2 Run the upgrade command with the system_upgrade tag:
openstack overcloud upgrade run --stack overcloud --tags system_upgrade --limit overcloud-controller-2
# 5.3 Run the upgrade command with no tags:
openstack overcloud upgrade run --stack overcloud --limit overcloud-controller-0,overcloud-controller-1,overcloud-controller-2
