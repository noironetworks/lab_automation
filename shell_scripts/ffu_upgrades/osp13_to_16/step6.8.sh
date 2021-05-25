############################################################################
# 6.8 Obtaining transitional containers for upgrades
############################################################################
# 1. Log in to your undercloud host as the stack user.
# 2. Edit the containers-prepare-parameter.yaml file.
# 3. Add the transitional container parameters to set in the ContainerImagePrepare parameter
#    (i.e. additional info is before the "ceph3_namespace" line, which is already present):
#
#       ...
vi /home/stack/templates/containers-prepare-parameter.yaml
#     ...
      name_prefix_stein: openstack-
      name_suffix_stein: ''
      namespace_stein: registry.redhat.io/rhosp15-rhel8
      tag_stein: 15.0
#     ceph3_namespace: registry.redhat.io/rhceph
#     ceph3_tag: latest
#     ceph3_image: rhceph-3-rhel7
#     ...
# 
# 4. Change the neutron_driver parameter to openvswitch:
        neutron_driver: openvswitch
# 4.5 Add container registry login parameters:
  ContainerImageRegistryCredentials:
     registry.redhat.io:
       mcohen2@cisco.com: <our password>
# 5. Save the containers-prepare-parameter.yaml file.
