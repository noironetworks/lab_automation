####################
# 4.7. NEXT STEPS
####################

# 1. (Re-)Build the containers used by Cisco
#/opt/ciscoaci-tripleo-heat-templates/tools/build_openstack_aci_containers.py -d 1.100.1.1:8787
/opt/ciscoaci-tripleo-heat-templates/tools/build_openstack_aci_containers.py -z /home/stack/openstack-ciscorpms-repo-13.0-1042.tar.gz -u $(ifconfig eth0 | grep 'inet ' | awk '{print $2}')  -d 1.100.1.1:8787
