############################################################################
# 9.3 Configuring access to the undercloud registry
############################################################################
# 1. Log in to the undercloud as the stack user.
# 2. Obtain the control plane host name on the undercloud:
export UCLOUD_HOST=$(sudo hiera container_image_prepare_node_names | awk -F'"' '{print $2}')
# 3. Edit the containers-prepare-parameter.yaml file and add the DockerInsecureRegistryAddress parameter with a YAML list that contains the control plane host name of the undercloud and the IP address of the undercloud on the provisioning network:
echo "  DockerInsecureRegistryAddress:" >> /home/stack/templates/containers-prepare-parameter.yaml
echo "  - ${UCLOUD_HOST}:8787" >> /home/stack/templates/containers-prepare-parameter.yaml
echo "  - 1.100.1.1:8787" >> /home/stack/templates/containers-prepare-parameter.yaml
echo "  - 10.30.120.22:8787" >> /home/stack/templates/containers-prepare-parameter.yaml
