export CONFIG=~/focal-yoga/yoga-opflex-sfc.yaml
juju upgrade-charm --config=$CONFIG  mysql
juju upgrade-charm --config=$CONFIG  rabbitmq-server
~/bin/cc-workload.sh
juju upgrade-charm --config=$CONFIG  keystone
juju upgrade-charm --config=$CONFIG  glance
juju upgrade-charm --path=/home/noiro/charms/bionic/charm-neutron-api --config=$CONFIG neutron-api
juju upgrade-charm --path=/home/noiro/charms/bionic/charm-neutron-api-plugin-aci --config=$CONFIG neutron-api-plugin-aci
~/bin/cc-workload.sh
juju upgrade-charm --path=/home/noiro/charms/bionic/charm-neutron-gateway --config=$CONFIG neutron-gateway
juju upgrade-charm --config=$CONFIG  nova-cloud-controller
juju upgrade-charm --config=$CONFIG  placement
juju upgrade-charm --config=$CONFIG  nova-compute
juju upgrade-charm --config=$CONFIG  openstack-dashboard
juju upgrade-charm --path=/home/noiro/charms/bionic/charm-openstack-dashboard-plugin-gbp --config=$CONFIG openstack-dashboard-plugin-gbp
~/bin/cc-workload.sh
juju ssh 2 sudo systemctl stop lldpd.service
juju ssh 3 sudo systemctl stop lldpd.service
juju ssh 4 sudo systemctl stop lldpd.service
juju upgrade-charm --path=/home/noiro/charms/bionic/charm-neutron-aci-opflex --config=$CONFIG neutron-aci-opflex

~/bin/cc-workload.sh
sleep 100
juju ssh 2 sudo systemctl start lldpd.service
juju ssh 3 sudo systemctl start lldpd.service
juju ssh 4 sudo systemctl start lldpd.service


juju refresh --config=$CONFIG  mysql
juju refresh --channel=yoga/stable --config=$CONFIG rabbitmq-server
~/bin/cc-workload.sh
juju refresh --channel=yoga/stable --config=$CONFIG keystone
juju refresh --channel=yoga/stable --config=$CONFIG glance
juju refresh --path=/home/noiro/charms/bionic/charm-neutron-api --config=$CONFIG neutron-api
juju refresh --path=/home/noiro/charms/bionic/charm-neutron-api-plugin-aci --config=$CONFIG neutron-api-plugin-aci
~/bin/cc-workload.sh
juju refresh --path=/home/noiro/charms/bionic/charm-neutron-gateway --config=$CONFIG neutron-gateway
juju refresh --channel=yoga/stable --config=$CONFIG  nova-cloud-controller
~/bin/cc-workload.sh
juju refresh --channel=yoga/stable --config=$CONFIG  placement
juju refresh --channel=yoga/stable  nova-compute
juju refresh --channel=yoga/stable --config=$CONFIG  openstack-dashboard
juju refresh --path=/home/noiro/charms/bionic/charm-openstack-dashboard-plugin-gbp --config=$CONFIG openstack-dashboard-plugin-gbp
~/bin/cc-workload.sh
juju ssh 2 sudo systemctl stop lldpd.service
juju ssh 3 sudo systemctl stop lldpd.service
juju ssh 4 sudo systemctl stop lldpd.service

juju refresh  --path=/home/noiro/charms/bionic/charm-neutron-aci-opflex --config=$CONFIG neutron-aci-opflex
~/bin/cc-workload.sh
sleep 100
juju ssh 2 sudo systemctl start lldpd.service
juju ssh 3 sudo systemctl start lldpd.service
juju ssh 4 sudo systemctl start lldpd.service
