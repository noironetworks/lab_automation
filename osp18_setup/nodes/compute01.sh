sudo cobbler system add \
--name fab205-compute01 \
--profile rhel9_4-x86_64 \
--netboot-enabled=true \
--autoinstall compute-ks.cfg \
--hostname compute01 \
--dns-name compute01.fab205.local \
--ip-address 1.100.1.101  \
--static=false \
--interface eno5 \
--netmask 255.255.255.0 \
--mac ec:f4:0c:43:e1:8e \
--gateway 1.100.1.1 \
--kernel-options="ip=eno1:dhcp:1500 ip=10.100.1.101::10.100.1.1:255.255.255.0:compute01.fab205.local:ens9f0.4001:none:9000 vlan=ens9f0.4001:ens9f0"
#--kernel-options="coreos.live.rootfs_url=http://1.100.1.1:8080/rootfs/rhcos-x86_64-4.16.3/rhcos-live-rootfs.x86_64.img coreos.inst.install_dev=/dev/sda coreos.inst.ignition_url=http://10.100.1.10:8080/ignition/fab205/bootstrap.ign ip=eno1:dhcp:1500 ip=10.100.1.17::10.100.1.1:255.255.255.0:bootstrap.fab205.local:ens9f0.4001:none:9000 vlan=ens9f0.4001:ens9f0"
