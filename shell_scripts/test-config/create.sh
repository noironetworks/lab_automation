openstack project create prj$1
openstack quota set --cores -1 prj$1
openstack quota set --fixed-ips -1 prj$1
openstack quota set --floating-ips -1 prj$1
openstack quota set --injected-file-size -1 prj$1
openstack quota set --injected-files -1 prj$1
openstack quota set --instances -1 prj$1
openstack quota set --key-pairs -1 prj$1
openstack quota set --properties -1 prj$1
openstack quota set --ram -1 prj$1
openstack quota set --server-groups -1 prj$1
openstack quota set --server-group-members -1 prj$1
openstack quota set --backups -1 prj$1
openstack quota set --backup-gigabytes -1 prj$1
openstack quota set --gigabytes -1 prj$1
openstack quota set --per-volume-gigabytes -1 prj$1
openstack quota set --snapshots -1 prj$1
openstack quota set --volumes -1 prj$1
openstack quota set --volume-type -1 prj$1
openstack quota set --secgroup-rules -1 prj$1
openstack quota set --secgroups -1 prj$1
openstack quota set --networks -1 prj$1
openstack quota set --subnets -1 prj$1
openstack quota set --ports -1 prj$1
openstack quota set --routers -1 prj$1
openstack quota set --rbac-policies -1 prj$1
openstack quota set --subnetpools -1 prj$1
openstack role add --user admin --project prj$1 admin
openstack --os-project-name prj$1 network create net$1
neutron --os-project-name prj$1 subnet-create net$1 40.40.40.0/24 --name subnet$1
neutron --os-project-name prj$1 router-create rtr$1
neutron --os-project-name prj$1 router-interface-add rtr$1 subnet=subnet$1
neutron --os-project-name prj$1 router-gateway-set rtr$1 sauto_l3out-2
openstack --os-project-name prj$1 security group create sg$1-1
openstack --os-project-name prj$1 security group create sg$1-2
for port in $(seq 100); do openstack --os-project-name prj$1 security group rule create --remote-group sg$1-2 --ingress --protocol tcp --dst-port $port sg$1-1; done
for port in $(seq 100); do openstack --os-project-name prj$1 security group rule create --remote-group sg$1-1 --ingress --protocol tcp --dst-port $port sg$1-2; done
SG1_ID=$(openstack --os-project-name prj$1 security group show sg$1-1 -c id -f value)
SG2_ID=$(openstack --os-project-name prj$1 security group show sg$1-2 -c id -f value)
nova --os-project-name prj$1 boot --security-groups $SG1_ID --nic net-name=net$1 --image cirros.new --flavor m1.tiny vm$1-1
nova --os-project-name prj$1 boot --security-groups $SG2_ID --nic net-name=net$1 --image cirros.new --flavor m1.tiny vm$1-2
