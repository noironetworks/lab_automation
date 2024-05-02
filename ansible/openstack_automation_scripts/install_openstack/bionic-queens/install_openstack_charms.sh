set -x
if [ $1 ]; then 
   no_proxy=$1 
fi

juju bootstrap fab8-cloud --bootstrap-series bionic --to juju --force --config no-proxy=$no_proxy --config  http-proxy=$http_proxy --config https-proxy=$https_proxy --config  snap-http-proxy=$http_proxy --config snap-https-proxy=$https_proxy
$HOME/openstack_automation_scripts/install_openstack/bionic-get-machines
$HOME/openstack_automation_scripts/install_openstack/mac-status

compute02_id=$(juju status | grep -E "$Compute02" | awk '{print $1}')
compute01_id=$(juju status | grep -E "$Compute01" | awk '{print $1}')
dashboard_id=$(juju status | grep -E "$dashboard" | awk '{print $1}')
controller_id=$(juju status | grep -E "$controller" | awk '{print $1}')
gateway_id=$(juju status | grep -E "$Gateway" | awk '{print $1}')

export CONFIG=$HOME/openstack_automation_scripts/install_openstack/bionic-queens/queens-opflex-sfc.yaml

#juju deploy --config=$CONFIG cs:xenial/mysql --to lxd:1
juju deploy --config=$CONFIG ch:bionic/percona-cluster mysql --to lxd:"$controller_id"
juju config mysql max-connections=1300
#juju deploy --config=$CONFIG cs:bionic/rabbitmq-server --to lxd:1
juju deploy  --config=$CONFIG rabbitmq-server --channel 3.8/stable  --series bionic --to lxd:"$controller_id"

$HOME/openstack_automation_scripts/install_openstack/app-status

juju deploy  --config=$CONFIG keystone --channel queens/candidate  --series bionic --to lxd:"$controller_id"
#juju deploy --config=$CONFIG cs:bionic/keystone --to lxd:1
juju add-relation keystone:shared-db mysql:shared-db

#juju deploy cs:bionic/glance --to lxd:1
juju deploy glance --channel queens/candidate  --series bionic --to lxd:"$controller_id"
juju add-relation glance:identity-service keystone:identity-service
juju add-relation glance:shared-db mysql:shared-db

juju deploy $HOME/charms/charm-neutron-api  --series bionic --config=$CONFIG neutron-api --to "$controller_id"
juju add-relation neutron-api:amqp rabbitmq-server:amqp
juju add-relation neutron-api:identity-service keystone:identity-service
juju add-relation neutron-api:shared-db mysql:shared-db

juju deploy $HOME/charms/charm-neutron-api-plugin-aci --series bionic --config=$CONFIG neutron-api-plugin-aci
juju add-relation neutron-api-plugin-aci neutron-api
juju add-relation neutron-api-plugin-aci:amqp rabbitmq-server:amqp
juju add-relation neutron-api-plugin-aci:shared-db mysql:shared-db


juju deploy $HOME/charms/charm-neutron-gateway --series bionic --config=$CONFIG neutron-gateway --to "$gateway_id"
juju add-relation neutron-gateway:amqp rabbitmq-server:amqp
juju add-relation neutron-gateway:neutron-plugin-api neutron-api:neutron-plugin-api


juju deploy --config=$CONFIG cs:bionic/nova-cloud-controller --to lxd:"$controller_id"
juju deploy --config=$CONFIG nova-cloud-controller --channel queens/candidate --series bionic  --to lxd:"$controller_id"
juju add-relation nova-cloud-controller:amqp rabbitmq-server:amqp
juju add-relation nova-cloud-controller:identity-service keystone:identity-service
juju add-relation nova-cloud-controller:image-service glance:image-service
juju add-relation nova-cloud-controller:neutron-api neutron-api:neutron-api
juju add-relation nova-cloud-controller:shared-db mysql:shared-db
juju add-relation nova-cloud-controller:quantum-network-service neutron-gateway:quantum-network-service

juju deploy  --config=$CONFIG nova-compute --channel queens/candidate --series bionic --to "$compute01_id"
#juju deploy --series bionic --config=$CONFIG cs:bionic/nova-compute --to 3
juju add-relation nova-compute:amqp rabbitmq-server:amqp
juju add-relation nova-compute:cloud-compute nova-cloud-controller:cloud-compute
juju add-relation nova-compute:image-service glance:image-service

#juju deploy --config=$CONFIG cs:bionic/openstack-dashboard --to 0
juju deploy --config=$CONFIG openstack-dashboard --channel queens/candidate  --series bionic --to "$dashboard_id"
juju add-relation openstack-dashboard:identity-service keystone:identity-service

juju deploy $HOME/charms/charm-openstack-dashboard-plugin-gbp --series bionic --config=$CONFIG openstack-dashboard-plugin-gbp
juju add-relation openstack-dashboard-plugin-gbp openstack-dashboard

juju add-unit nova-compute --to "$compute02_id"

$HOME/openstack_automation_scripts/install_openstack/cc-status
juju deploy $HOME/charms/charm-neutron-aci-opflex --series bionic --config=$CONFIG neutron-aci-opflex
juju add-relation neutron-aci-opflex:neutron-plugin-api neutron-api:neutron-plugin-api
juju add-relation neutron-aci-opflex:neutron-plugin nova-compute:neutron-plugin
juju add-relation neutron-aci-opflex:amqp rabbitmq-server:amqp
juju add-relation neutron-aci-opflex:aci-opflex neutron-gateway:aci-opflex
juju add-relation neutron-aci-opflex:quantum-network-service neutron-gateway:quantum-network-service

$HOME/openstack_automation_scripts/install_openstack/app-status

juju deploy $HOME/charms/charm-openstack-dashboard-plugin-gbp --series bionic --config=$CONFIG openstack-dashboard-plugin-gbp
juju add-relation openstack-dashboard-plugin-gbp openstack-dashboard

#juju ssh 1 sudo patch /usr/lib/python2.7/dist-packages/gbpservice/neutron/plugins/ml2plus/drivers/apic_aim/mechanism_driver.py < svi_dhcp_patch.txt
juju ssh 1 sudo apt-get -y install python-networking-sfc
juju ssh 1 sudo neutron-db-manage upgrade head
juju ssh 1 sudo service neutron-server restart
$HOME/openstack_automation_scripts/install_openstack/make-openrc

