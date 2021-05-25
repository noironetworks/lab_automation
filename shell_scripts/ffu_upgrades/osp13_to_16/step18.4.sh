############################################################################
# 18.4 Upgrading Compute nodes
############################################################################
# 1. Source the stackrc file:
source ~/stackrc
# 1.1 Fix /etc/resolv.conf on overcloud hosts (gets lost after node reboot)
export COMPUTE_IP=$(openstack server list  -c Name -f value -c Networks -f value |grep compute-0  | awk -F"=" '{print $2}')
ssh heat-admin@$COMPUTE_IP
sudo -s
echo "nameserver 172.28.184.18" >> /etc/resolv.conf
exit
exit
export COMPUTE_IP=$(openstack server list  -c Name -f value -c Networks -f value |grep compute-1  | awk -F"=" '{print $2}')
ssh heat-admin@$COMPUTE_IP
sudo -s
echo "nameserver 172.28.184.18" >> /etc/resolv.conf
exit
exit
# 2. Migrate your instances. 
# 3. Run the upgrade command with the system_upgrade tag:
#openstack overcloud upgrade run --stack overcloud --tags system_upgrade --limit overcloud-compute-0
# 4. Run the upgrade command with no tags:
#openstack overcloud upgrade run --stack overcloud --limit overcloud-compute-0
# 5. To upgrade multiple Compute nodes in parallel, set the --limit option to a comma-separated list of nodes that you want to upgrade. First perform the system_upgrade task:
openstack overcloud upgrade run --stack overcloud --tags system_upgrade --limit overcloud-compute-0,overcloud-compute-1
# 5.1 Remove RHEL7 repos from yum configuration on overcloud hosts
sudo -s
export COMPUTE_IP=$(openstack server list  -c Name -f value -c Networks -f value |grep compute-0  | awk -F"=" '{print $2}')
ssh heat-admin@$COMPUTE_IP
sudo -s
vi /etc/yum.repos.d/localrepo.repo
exit
exit
export COMPUTE_IP=$(openstack server list  -c Name -f value -c Networks -f value |grep compute-1  | awk -F"=" '{print $2}')
ssh heat-admin@$COMPUTE_IP
sudo -s
vi /etc/yum.repos.d/localrepo.repo
exit
exit
# Then perform the standard OpenStack service upgrade:
openstack overcloud upgrade run --stack overcloud  --limit overcloud-compute-0,overcloud-compute-1
