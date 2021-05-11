#######################################################
# 2.12. VALIDATING AN OPENSTACK PLATFORM 10 OVERCLOUD
#######################################################

# 1. Source the undercloud access details
source ~/stackrc
# 2. Check the status of your bare metal nodes
openstack baremetal node list
# 3. Check for failed Systemd services
for NODE in $(openstack server list -f value -c Networks | cut -d= -f2); do echo "=== $NODE ===" ; ssh heat-admin@$NODE "sudo systemctl list-units --state=failed 'openstack*' 'neutron*' 'httpd' 'docker' 'ceph*'" ; done
# 4. Check the HAProxy connection to all services.
## 4a. Obtain the Control Plane VIP address and authentication details for the haproxy.stats service
NODE=$(openstack server list --name controller-0 -f value -c Networks | cut -d= -f2); ssh heat-admin@$NODE sudo 'grep "listen haproxy.stats" -A 6 /etc/haproxy/haproxy.cfg'
## 4b. Use these details in the following cURL request
curl -s -u admin:<PASSWORD> "http://<IP ADDRESS>:1993/;csv" | egrep -vi "(frontend|backend)" | awk -F',' '{ print $1" "$2" "$18 }'
# 5. Check overcloud database replication health
for NODE in $(openstack server list --name controller -f value -c Networks | cut -d= -f2); do echo "=== $NODE ===" ; ssh heat-admin@$NODE "sudo clustercheck" ; done
# 6. Check RabbitMQ cluster health
for NODE in $(openstack server list --name controller -f value -c Networks | cut -d= -f2); do echo "=== $NODE ===" ; ssh heat-admin@$NODE "sudo rabbitmqctl node_health_check"; done
# 7. Check Pacemaker resource health
NODE=$(openstack server list --name controller-0 -f value -c Networks | cut -d= -f2); ssh heat-admin@$NODE "sudo pcs status"
# 8. Check the disk space on each overcloud node
for NODE in $(openstack server list -f value -c Networks | cut -d= -f2); do echo "=== $NODE ===" ; ssh heat-admin@$NODE "sudo df -h --output=source,fstype,avail -x overlay -x tmpfs -x devtmpfs" ; done
# 9. Check overcloud Ceph Storage cluster health. The following command runs the ceph tool on a
#    Controller node to check the cluster:
NODE=$(openstack server list --name controller-0 -f value -c Networks | cut -d= -f2); ssh heat-admin@$NODE "sudo ceph -s"
# 10. Check Ceph Storage OSD for free space. The following command runs the ceph tool on a
#     Controller node to check the free space
NODE=$(openstack server list --name controller-0 -f value -c Networks | cut -d= -f2); ssh heat-admin@$NODE "sudo ceph df"
# 11. Check that clocks are synchronized on overcloud nodes
for NODE in $(openstack server list -f value -c Networks | cut -d= -f2); do echo "=== $NODE ===" ; ssh heat-admin@$NODE "sudo ntpstat" ; done
# 12. Source the overcloud access details
source ~/overcloudrc
# 13. Check the overcloud network services
openstack network agent list
# 14. Check the overcloud compute services
openstack compute service list
# 15. Check the overcloud volume services
openstack volume service lis
