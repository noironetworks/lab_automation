openstack --os-project-name prj$1 server delete vm$1-1
openstack --os-project-name prj$1 server delete vm$1-2
openstack --os-project-name prj$1 security group delete sg$1-1
openstack --os-project-name prj$1 security group delete sg$1-2
neutron --os-project-name prj$1 router-gateway-clear rtr$1
neutron --os-project-name prj$1 router-interface-delete rtr$1 subnet=subnet$1
neutron --os-project-name prj$1 router-delete rtr$1
neutron --os-project-name prj$1 subnet-delete subnet$1
openstack --os-project-name prj$1 network delete net$1
openstack project delete prj$1
