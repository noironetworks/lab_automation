##################################################################
# 5.16 CONVERTING NETWORK INTERFACE TEMPLATES TO THE NEW STRUCTURE
##################################################################
/usr/share/openstack-tripleo-heat-templates/tools/yaml-nic-config-2-script.py \
    --script-dir /usr/share/openstack-tripleo-heat-templates/network/scripts \
    compute.yaml compute.yaml
/usr/share/openstack-tripleo-heat-templates/tools/yaml-nic-config-2-script.py \
    --script-dir /usr/share/openstack-tripleo-heat-templates/network/scripts \
    controller.yaml controller.yaml
