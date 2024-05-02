
juju bootstrap '$cloud' --bootstrap-series=jammy --to '$juju' --config no-proxy=$no_proxy --config http-proxy=$http_proxy --config https-proxy=$https_proxy --config  snap-http-proxy=$http_proxy --config snap-https-proxy=$https_proxy

juju add-machine '$dashboard'.maas  --series jammy
sleep 20
juju add-machine '$controller'.maas  --series jammy
sleep 20
juju add-machine '$Compute01'.maas  --series jammy
sleep 20
juju add-machine '$Compute02'.maas  --series jammy

check_machines_status() {
    MACHINES=0

    while [ $MACHINES -eq 0 ]; do
        for i in $(juju machines --format json | jq '.machines[].["juju-status"].current'); do
            if [ "$i" = "\"started\"" ]; then
                MACHINES=1
            else
                MACHINES=0
                break
            fi
        done
        sleep 5
    done
}

check_machines_status


compute02_id=$(juju status | grep -E '$Compute02' | awk '{print $1}')
compute01_id=$(juju status | grep -E '$Compute01' | awk '{print $1}')
dashboard_id=$(juju status | grep -E '$dashboard' | awk '{print $1}')
controller_id=$(juju status | grep -E '$controller' | awk '{print $1}')

export CONFIG=~/install_antelope/antelope_opflex_sfc.yaml

juju deploy -n 3 --to lxd:"$controller_id",lxd:"$compute01_id",lxd:"$compute02_id" --channel 8.0/stable mysql-innodb-cluster
juju deploy -n 2 --to "$compute01_id","$compute02_id" --channel 2023.1/stable --config $CONFIG nova-compute

juju deploy --to lxd:"$controller_id" --channel 1.8/stable vault

juju deploy --channel 8.0/stable mysql-router vault-mysql-router
juju add-relation vault-mysql-router:db-router mysql-innodb-cluster:db-router
juju add-relation vault-mysql-router:shared-db vault:shared-db

sudo snap install vault

check_vault_status() {
    while true; do
        status=$(juju status | awk '/vault\/[0-9]+/ {print $2}')

        if [ "$status" == "blocked" ] || [ "$status" == "active" ]; then
            echo "Vault is $status"
            break
        else
            echo "Vault status is $status, waiting..."
            sleep 10 
        fi
    done
}

check_vault_status
initialize_vault() {

    vault_address=$(juju status | awk '/vault\/[0-9]+/ {print $5}')
    export VAULT_ADDR="http://$vault_address:8200"

    # Check if VAULT_ADDR is set
    if [ -z "$VAULT_ADDR" ]; then
        echo "Error: VAULT_ADDR is not set. Exiting."
        return 1
    fi

    # Initialize Vault
    vault operator init -key-shares=5 -key-threshold=3 > vault_init.txt 

    # Extract unseal keys and initial root token from the output
    unseal_keys=$(grep "Unseal Key" vault_init.txt | awk '{print $NF}')
    initial_root_token=$(grep "Initial Root Token" vault_init.txt | awk '{print $NF}')

    # Unseal Vault using the first three unseal keys
    for ((i = 1; i <= 3; i++)); do
        key=$(echo "$unseal_keys" | sed -n "${i}p")
        echo "Unsealing with key: $key"
        vault operator unseal "$key"
    done

    sleep 10
    check_vault_status
    # Set the initial root token
    export VAULT_TOKEN="$initial_root_token"
    echo "$VAULT_TOKEN"

    # Check if VAULT_TOKEN is set
    if [ -z "$VAULT_TOKEN" ]; then
        echo "Error: VAULT_TOKEN is not set. Exiting."
        return 1
    fi

    # Create a new token with a TTL of 10 minutes
    new_token=$(vault token create -ttl=10m -format=json | jq -r '.auth.client_token')

    # Authorize the new token with the Vault leader charm
    echo "Authorize with token: $new_token"
    juju run-action --wait vault/leader authorize-charm token="$new_token"
}

initialize_vault

juju run-action --wait vault/leader generate-root-ca

juju add-relation mysql-innodb-cluster:certificates vault:certificates

# create br-ex bridge with external network

juju deploy -n 3 --to lxd:"$controller_id",lxd:"$compute01_id",lxd:"$compute02_id" --channel 23.03/stable ovn-central

juju deploy --to lxd:"$controller_id" --channel 2023.1/stable --config $CONFIG neutron-api

juju deploy --channel 2023.1/stable neutron-api-plugin-ovn
juju deploy --channel 23.03/stable --config $CONFIG ovn-chassis

juju add-relation neutron-api-plugin-ovn:neutron-plugin neutron-api:neutron-plugin-api-subordinate
juju add-relation neutron-api-plugin-ovn:ovsdb-cms ovn-central:ovsdb-cms
juju add-relation ovn-chassis:ovsdb ovn-central:ovsdb
juju add-relation ovn-chassis:nova-compute nova-compute:neutron-plugin
juju add-relation neutron-api:certificates vault:certificates
juju add-relation neutron-api-plugin-ovn:certificates vault:certificates
juju add-relation ovn-central:certificates vault:certificates
juju add-relation ovn-chassis:certificates vault:certificates

#start
juju deploy --channel 8.0/stable mysql-router neutron-api-mysql-router
juju add-relation neutron-api-mysql-router:db-router mysql-innodb-cluster:db-router
juju add-relation neutron-api-mysql-router:shared-db neutron-api:shared-db

juju deploy --to lxd:"$controller_id" --channel 2023.1/stable keystone

juju deploy --channel 8.0/stable mysql-router keystone-mysql-router
juju add-relation keystone-mysql-router:db-router mysql-innodb-cluster:db-router
juju add-relation keystone-mysql-router:shared-db keystone:shared-db

juju add-relation keystone:identity-service neutron-api:identity-service
juju add-relation keystone:certificates vault:certificates

juju deploy --to lxd:"$controller_id" --channel 3.9/stable rabbitmq-server

juju add-relation rabbitmq-server:amqp neutron-api:amqp
juju add-relation rabbitmq-server:amqp nova-compute:amqp

juju deploy --to lxd:"$controller_id" --channel 2023.1/stable --config $CONFIG nova-cloud-controller

juju deploy --channel 8.0/stable mysql-router ncc-mysql-router
juju add-relation ncc-mysql-router:db-router mysql-innodb-cluster:db-router
juju add-relation ncc-mysql-router:shared-db nova-cloud-controller:shared-db

juju add-relation nova-cloud-controller:identity-service keystone:identity-service
juju add-relation nova-cloud-controller:amqp rabbitmq-server:amqp
juju add-relation nova-cloud-controller:neutron-api neutron-api:neutron-api
juju add-relation nova-cloud-controller:cloud-compute nova-compute:cloud-compute
juju add-relation nova-cloud-controller:certificates vault:certificates

juju deploy --to lxd:"$controller_id" --channel 2023.1/stable placement

juju deploy --channel 8.0/stable mysql-router placement-mysql-router
juju add-relation placement-mysql-router:db-router mysql-innodb-cluster:db-router
juju add-relation placement-mysql-router:shared-db placement:shared-db

juju add-relation placement:identity-service keystone:identity-service
juju add-relation placement:placement nova-cloud-controller:placement
juju add-relation placement:certificates vault:certificates

juju deploy --to "$dashboard_id" --channel 2023.1/stable openstack-dashboard

juju deploy --channel 8.0/stable mysql-router dashboard-mysql-router
juju add-relation dashboard-mysql-router:db-router mysql-innodb-cluster:db-router
juju add-relation dashboard-mysql-router:shared-db openstack-dashboard:shared-db

juju add-relation openstack-dashboard:identity-service keystone:identity-service
juju add-relation openstack-dashboard:certificates vault:certificates

sleep 180
juju deploy --to lxd:"$controller_id" --channel 2023.1/stable glance

juju deploy --channel 8.0/stable mysql-router glance-mysql-router
juju add-relation glance-mysql-router:db-router mysql-innodb-cluster:db-router
juju add-relation glance-mysql-router:shared-db glance:shared-db

juju add-relation glance:image-service nova-cloud-controller:image-service
juju add-relation glance:image-service nova-compute:image-service
juju add-relation glance:identity-service keystone:identity-service
juju add-relation glance:certificates vault:certificates

juju deploy --to lxd:"$dashboard_id" --channel 2023.1/stable --config $CONFIG cinder

juju deploy --channel 8.0/stable mysql-router cinder-mysql-router
juju add-relation cinder-mysql-router:db-router mysql-innodb-cluster:db-router
juju add-relation cinder-mysql-router:shared-db cinder:shared-db
juju add-relation cinder:cinder-volume-service nova-cloud-controller:cinder-volume-service
juju add-relation cinder:identity-service keystone:identity-service
juju add-relation cinder:amqp rabbitmq-server:amqp
juju add-relation cinder:image-service glance:image-service
juju add-relation cinder:certificates vault:certificates

check_status() {
    STATUS=0

    while [ $STATUS -eq 0 ]; do
        for status in $(juju status --format=json | jq '.applications[].["application-status"].current'); do
            if [ "$status" = "\"active\"" ] || [ "$status" = "\"unknown\"" ]; then
                STATUS=1
            else
                STATUS=0
                break
            fi
        done
        sleep 5
    done
}

check_status


{
	echo "Public address for openstack-dashboard:"
	ip_address=$(juju status --format=yaml openstack-dashboard | grep public-address | awk '{print $2}' | head -1)
	url="http://$ip_address/horizon"
	echo "$url"
	echo
        echo "Admin password for Keystone leader unit:"
        juju run --unit keystone/leader leader-get admin_passwd

} > dashboard_cred.txt

echo "Dashboard credentials added in dashboard_cred file"
sudo snap install openstackclients

git clone https://github.com/openstack-charmers/openstack-bundles ~/openstack-bundles
source ~/openstack-bundles/stable/openstack-base/openrc     

juju run -m default --unit vault/leader 'leader-get root-ca'
juju run -m default --unit keystone/leader 'leader-get admin_passwd'

echo "source ~/openstack-bundles/stable/openstack-base/openrc" > ~/openrc
