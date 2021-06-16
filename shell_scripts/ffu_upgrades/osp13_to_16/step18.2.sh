############################################################################
# 18.2 Upgrading Controller nodes with director-deployed Ceph Storage
############################################################################
# 1. Source the stackrc file:
source ~/stackrc
# 2. Identify the bootstrap Controller node by running the following command on a Controller node:
#sudo hiera -c /etc/puppet/hiera.yaml pacemaker_short_bootstrap_node_name
# To run this command from the undercloud, run the following SSH command and substitute CONTROLLER_IP with the IP address of any Controller node in your environment:
export CONTROLLER_IP=$(openstack server list  -c Name -f value -c Networks -f value |grep controller-0  | awk -F"=" '{print $2}')
ssh heat-admin@$CONTROLLER_IP "sudo hiera -c /etc/puppet/hiera.yaml pacemaker_short_bootstrap_node_name"
# 2.5 Fix /etc/resolv.conf on overcloud host (gets lost after node reboot)
ssh heat-admin@$CONTROLLER_IP
sudo -s
echo "nameserver 172.28.184.18" >> /etc/resolv.conf
exit
exit
# 3. Upgrade the bootstrap Controller node:
# 3.1 Run the external upgrade command with the ceph_systemd tag:
#openstack overcloud external-upgrade run --stack overcloud --tags ceph_systemd -e ceph_ansible_limit=overcloud-controller-0
# 3.2 Run the upgrade command with the system_upgrade tag:
openstack overcloud upgrade run --stack overcloud --tags system_upgrade --limit overcloud-controller-0
# 3.3 Run the external upgrade command with the system_upgrade_transfer_data tag:
openstack overcloud external-upgrade run --stack overcloud --tags system_upgrade_transfer_data
# 3.4 Run the upgrade command with the nova_hybrid_state tag and run only the upgrade_steps_playbook.yaml playbook:
openstack overcloud upgrade run --stack overcloud --playbook upgrade_steps_playbook.yaml --tags nova_hybrid_state --limit all
# 3.4.1 Remove RHEL7 repos from yum configuration on overcloud hosts
ssh heat-admin@$CONTROLLER_IP
sudo -s
vi /etc/yum.repos.d/localrepo.repo
exit
exit
# 3.5 Run the upgrade command with no tags:
openstack overcloud upgrade run --stack overcloud --limit overcloud-controller-0
# 3.5.1 This step often fails. If it does, log in to the controller, run "sudo ifup ext-br", and re-run the last step.
# 4. Upgrade the next Controller node:
# 4.0 Fix /etc/resolv.conf on overcloud host (gets lost after node reboot)
export CONTROLLER_IP=$(openstack server list  -c Name -f value -c Networks -f value |grep controller-1  | awk -F"=" '{print $2}')
ssh heat-admin@$CONTROLLER_IP
sudo -s
echo "nameserver 172.28.184.18" >> /etc/resolv.conf
exit
exit
# 4.1 Run the external upgrade command with the ceph_systemd tag:
#openstack overcloud external-upgrade run --stack overcloud --tags ceph_systemd -e ceph_ansible_limit=overcloud-controller-1
# 4.2 Run the upgrade command with the system_upgrade tag on the next Controller node:
openstack overcloud upgrade run --stack overcloud --tags system_upgrade --limit overcloud-controller-1
# 4.2.1 Remove RHEL7 repos from yum configuration on overcloud hosts
ssh heat-admin@$CONTROLLER_IP
sudo -s
vi /etc/yum.repos.d/localrepo.repo
exit
exit
# 4.3 Run the upgrade command with no tags:
openstack overcloud upgrade run --stack overcloud --limit overcloud-controller-0,overcloud-controller-1
# 4.3.1 This step often fails. If it does, log in to the controller, run "sudo ifup ext-br", and re-run the last step.
# 5. Upgrade the final Controller node:
# 5.0 Fix /etc/resolv.conf on overcloud host (gets lost after node reboot)
export CONTROLLER_IP=$(openstack server list  -c Name -f value -c Networks -f value |grep controller-2  | awk -F"=" '{print $2}')
ssh heat-admin@$CONTROLLER_IP
sudo -s
echo "nameserver 172.28.184.18" >> /etc/resolv.conf
exit
exit
# 5.1 Run the external upgrade command with the ceph_systemd tag:
#openstack overcloud external-upgrade run --stack overcloud --tags ceph_systemd -e ceph_ansible_limit=overcloud-controller-2
# 5.2 Run the upgrade command with the system_upgrade tag:
openstack overcloud upgrade run --stack overcloud --tags system_upgrade --limit overcloud-controller-2
# 5.2.1 Remove RHEL7 repos from yum configuration on overcloud hosts
ssh heat-admin@$CONTROLLER_IP
sudo -s
vi /etc/yum.repos.d/localrepo.repo
exit
exit
# 5.3 Run the upgrade command with no tags:
openstack overcloud upgrade run --stack overcloud --limit overcloud-controller-0,overcloud-controller-1,overcloud-controller-2
# 5.3.1 This step often fails. If it does, log in to the controller, run "sudo ifup ext-br", and re-run the last step.
