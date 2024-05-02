source ~/openrc     
# confirm the use environment
openstack endpoint list --interface admin

# create image and flavor
mkdir -p ~/cloud-images

# image create
wget http://cloud-images.ubuntu.com/jammy/current/jammy-server-cloudimg-amd64.img \
	-O ~/cloud-images/jammy-amd64.img
wget http://download.cirros-cloud.net/0.3.5/cirros-0.3.5-x86_64-disk.img \
	-O ~/cloud-images/cirros-0.3.5-x86_64-disk.img

openstack image create --public --container-format bare \
   --disk-format qcow2 --file ~/cloud-images/cirros-0.3.5-x86_64-disk.img \
   cirros
openstack image create --public --container-format bare \
	--disk-format qcow2 --file ~/cloud-images/jammy-amd64.img \
	jammy

openstack flavor create --ram 512 --disk 1 --ephemeral 1 m1.tiny
openstack flavor create --ram 1024 --disk 21 --ephemeral 1 m1.small
# network and subnets create

openstack network create --internal user1_net
openstack network create --internal user2_net

openstack subnet create --network user1_net  \
   --subnet-range 192.168.0.0/24 \
   --allocation-pool start=192.168.0.10,end=192.168.0.99 \
   user1_subnet
openstack subnet create --network user2_net  \
   --subnet-range 192.168.1.0/24 \
   --allocation-pool start=192.168.1.10,end=192.168.1.99 \
   user2_subnet

#server create
openstack server create --image cirros --flavor m1.tiny --network user1_net test1-1
openstack server create --image cirros --flavor m1.tiny --network user1_net test1-2
openstack server create --image cirros --flavor m1.tiny --network user2_net test2-1
openstack server create --image cirros --flavor m1.tiny --network user2_net test2-2

# router create
openstack router create user1_router
openstack router add subnet user1_router user1_subnet
openstack router add subnet user1_router user2_subnet

# #extrnal network create & traffic flow
# openstack network create --external --share \
#     --provider-network-type flat --provider-physical-network physnet1 \
#     ext_net
    
# openstack subnet create --network ext_net --no-dhcp \
#   --gateway 10.246.112.1 --subnet-range 10.246.112.0/21 \
#   --allocation-pool start=10.246.116.23,end=10.246.116.87 \
#   ext_subnet
   
# openstack router set user1_router --external-gateway ext_net
# openstack security group rule create --proto tcp --dst-port 22 default
# openstack security group rule create --protocol icmp --ingress default
# FLOATING_IP1=$(openstack floating ip create -f value -c floating_ip_address ext_net)
# openstack server add floating ip test1-1 $FLOATING_IP
# FLOATING_IP2=$(openstack floating ip create -f value -c floating_ip_address ext_net)
# openstack server add floating ip test1-2 $FLOATING_IP
# FLOATING_IP3=$(openstack floating ip create -f value -c floating_ip_address ext_net)
# openstack server add floating ip test2-1 $FLOATING_IP
# FLOATING_IP4=$(openstack floating ip create -f value -c floating_ip_address ext_net)
# openstack server add floating ip test2-2 $FLOATING_IP

# password="cubswin:)"
# sshpass -p "$password" ssh cirros@"$FLOATING_IP1" "ping -c 4 $FLOATING_IP3 && ping -c 4 $FLOATING_IP2 && ping -c 4 $FLOATING_IP4"
# sshpass -p "$password" ssh cirros@"$FLOATING_IP3" "ping -c 4 $FLOATING_IP2 && ping -c 4 $FLOATING_IP1 && ping -c 4 $FLOATING_IP4"
