sh ./ff-upgrades/step0.sh
for server in $(openstack server list -f value -c Networks | awk -F"=" '{print $2}'); do scp ff-upgrades/step0.sh heat-admin@$server: && ssh heat-admin@$server sh ./step0.sh; done
