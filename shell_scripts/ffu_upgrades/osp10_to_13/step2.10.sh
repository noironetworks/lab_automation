##################################
# 2.10. VERIFYING SYSTEM PACKAGES
##################################

# 1. Log into a node
# 2. Run yum to check the system packages
sudo yum list qemu-img-rhev qemu-kvm-common-rhev qemu-kvm-rhev qemu-kvm-toolsrhev openvswitch
# 3. Run ovs-vsctl to check the version currently running
# 4. Repeat these steps for all nodes
