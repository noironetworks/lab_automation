############################################################################
# 7.4 Disabling fencing in the overcloud
############################################################################
# 1. Log in to the undercloud as the stack user.
# 2. Source the stackrc file.
source ~/stackrc
# 3. Log in to a Controller node and run the Pacemaker command to disable fencing:
ssh heat-admin@$(openstack server list  -c Name -f value -c Networks -f value |grep controller-0  | awk -F"=" '{print $2}') "sudo pcs property set stonith-enabled=false"

