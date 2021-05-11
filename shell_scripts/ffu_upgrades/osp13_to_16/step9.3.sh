############################################################################
# 9.3 Configuring access to the undercloud registry
############################################################################
# 1. Log in to the undercloud as the stack user.
# 2. Obtain the control plane host name on the undercloud:
sudo hiera container_image_prepare_node_names
# 3. Edit the containers-prepare-parameter.yaml file and add the DockerInsecureRegistryAddress parameter with a YAML list that contains the control plane host name of the undercloud and the IP address of the undercloud on the provisioning network:
#parameter_defaults:
#  DockerInsecureRegistryAddress:
#  - undercloud.ctlplane.localdomain:8787
#  - 192.168.24.1:8787
  ...
