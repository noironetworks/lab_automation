# 0 = juju, 1 = controller, 2 = network, 3 = compute1, 4 = compute2
# controller should host extra ones likee, vault, nova-cloud-controller, placement, etc.
# network and 2 computes have PCI cards for fabric connectivity, neutron stuff should be hosted there
# even dashboard if possible
# nova compute services only go to compute nodes

juju bootstrap maas --bootstrap-series=jammy --to juju --config no-proxy=$no_proxy --config http-proxy=$http_proxy --config https-proxy=$https_proxy --config  snap-http-proxy=$http_proxy --config snap-https-proxy=$https_proxy
juju switch controller

sh ~/bin/jammy-get-machines

export CONFIG=~/antelope_new/antelope_config.yaml

juju deploy -n 3 --to lxd:1,lxd:2,lxd:3 --channel 8.0/stable mysql-innodb-cluster
juju deploy -n 2 --to 3,4 --channel 2023.1/stable --config $CONFIG nova-compute



juju deploy --to lxd:1 --channel 1.8/stable vault

#setup vault

# vault init (Manual steps) https://opendev.org/openstack/charm-vault/src/branch/stable/1.8/src/README.md#post-deployment-tasks
juju snap install vault
#export VAULT_ADDR="http://<vault charm adress>:8200"
export VAULT_ADDR="http://10.0.0.240:8200"

vault operator init -key-shares=5 -key-threshold=3

#Note down the keys and token produced
#

#
#Vault initialized with 5 key shares and a key threshold of 3. Please securely
#distribute the key shares printed above. When the Vault is re-sealed,
#restarted, or stopped, you must supply at least 3 of these keys to unseal it
#before it can start servicing requests.
#
#Vault does not store the generated root key. Without at least 3 keys to
#reconstruct the root key, Vault will remain permanently sealed!
#
#It is possible to generate new unseal keys, provided you have a quorum of
#existing unseal keys shares. See "vault operator rekey" for more information.
#Unseal Key 1: 
#Unseal Key 2: 
#Unseal Key 3: 
#Unseal Key 4: 
#Unseal Key 5: 
                                                                                                                                                                                                                       
#Initial Root Token: 
# run vault operator unseal <Key>
# with first three keys

# vault operator unseal 
# vault operator unseal 
# vault operator unseal 

# export VAULT_TOKEN=<Created token>
# Create token
# vault token create -ttl=60m
#
#Key                  Value
#---                  -----
#token                
#token_accessor       
#token_duration       1h
#token_renewable      true
#token_policies       ["root"]
#identity_policies    []
#policies             ["root"]

# Now authorize charms
# juju run vault/leader authorize-charm token=<token created above>
# juju run vault/leader generate-root-ca

juju deploy --channel 8.0/stable mysql-router vault-mysql-router
juju integrate vault-mysql-router:db-router mysql-innodb-cluster:db-router
juju integrate vault-mysql-router:shared-db vault:shared-db


juju deploy -n 3 --to lxd:2,lxd:3,lxd:4 --channel 23.03/stable ovn-central

juju deploy --to lxd:2 --channel 2023.1/stable --config $CONFIG neutron-api

juju deploy --channel 2023.1/stable neutron-api-plugin-ovn

juju deploy --channel 23.03/stable --config $CONFIG ovn-chassis


juju integrate neutron-api-plugin-ovn:neutron-plugin neutron-api:neutron-plugin-api-subordinate
juju integrate neutron-api-plugin-ovn:ovsdb-cms ovn-central:ovsdb-cms
juju integrate ovn-chassis:ovsdb ovn-central:ovsdb
juju integrate ovn-chassis:nova-compute nova-compute:neutron-plugin
juju integrate neutron-api:certificates vault:certificates
juju integrate neutron-api-plugin-ovn:certificates vault:certificates
juju integrate ovn-central:certificates vault:certificates
juju integrate ovn-chassis:certificates vault:certificates

juju deploy --channel 8.0/stable mysql-router neutron-api-mysql-router
juju integrate neutron-api-mysql-router:db-router mysql-innodb-cluster:db-router
juju integrate neutron-api-mysql-router:shared-db neutron-api:shared-db

juju deploy --to lxd:1 --channel 2023.1/stable keystone

juju deploy --channel 8.0/stable mysql-router keystone-mysql-router
juju integrate keystone-mysql-router:db-router mysql-innodb-cluster:db-router
juju integrate keystone-mysql-router:shared-db keystone:shared-db

juju integrate keystone:identity-service neutron-api:identity-service
juju integrate keystone:certificates vault:certificates


juju deploy --to lxd:1 --channel 3.9/stable rabbitmq-server

juju integrate rabbitmq-server:amqp neutron-api:amqp
juju integrate rabbitmq-server:amqp nova-compute:amqp

juju deploy --to lxd:1 --channel 2023.1/stable --config $CONFIG nova-cloud-controller

juju deploy --channel 8.0/stable mysql-router ncc-mysql-router
juju integrate ncc-mysql-router:db-router mysql-innodb-cluster:db-router
juju integrate ncc-mysql-router:shared-db nova-cloud-controller:shared-db

juju integrate nova-cloud-controller:identity-service keystone:identity-service
juju integrate nova-cloud-controller:amqp rabbitmq-server:amqp
juju integrate nova-cloud-controller:neutron-api neutron-api:neutron-api
juju integrate nova-cloud-controller:cloud-compute nova-compute:cloud-compute
juju integrate nova-cloud-controller:certificates vault:certificates


juju deploy --to lxd:1 --channel 2023.1/stable placement

juju deploy --channel 8.0/stable mysql-router placement-mysql-router
juju integrate placement-mysql-router:db-router mysql-innodb-cluster:db-router
juju integrate placement-mysql-router:shared-db placement:shared-db

juju integrate placement:identity-service keystone:identity-service
juju integrate placement:placement nova-cloud-controller:placement
juju integrate placement:certificates vault:certificates


#--

juju deploy --to lxd:0 --channel 2023.1/stable openstack-dashboard

juju deploy --channel 8.0/stable mysql-router dashboard-mysql-router
juju integrate dashboard-mysql-router:db-router mysql-innodb-cluster:db-router
juju integrate dashboard-mysql-router:shared-db openstack-dashboard:shared-db

juju integrate openstack-dashboard:identity-service keystone:identity-service
juju integrate openstack-dashboard:certificates vault:certificates

juju deploy --to lxd:1 --channel 2023.1/stable glance

juju deploy --channel 8.0/stable mysql-router glance-mysql-router
juju integrate glance-mysql-router:db-router mysql-innodb-cluster:db-router
juju integrate glance-mysql-router:shared-db glance:shared-db

juju integrate glance:image-service nova-cloud-controller:image-service
juju integrate glance:image-service nova-compute:image-service
juju integrate glance:identity-service keystone:identity-service
juju integrate glance:certificates vault:certificates

juju deploy --to lxd:1 --channel 2023.1/stable --config $CONFIG  cinder

juju deploy --channel 8.0/stable mysql-router cinder-mysql-router
juju integrate cinder-mysql-router:db-router mysql-innodb-cluster:db-router
juju integrate cinder-mysql-router:shared-db cinder:shared-db

juju integrate cinder:cinder-volume-service nova-cloud-controller:cinder-volume-service
juju integrate cinder:identity-service keystone:identity-service
juju integrate cinder:amqp rabbitmq-server:amqp
juju integrate cinder:image-service glance:image-service
juju integrate cinder:certificates vault:certificates


# post config
git clone https://github.com/openstack-charmers/openstack-bundles ~/openstack-bundles 
