############################################################################
# 9.5 Setting the Compute name format
############################################################################
# 1. Log in to the undercloud as the stack user.
# 2. Set the Compute naming format:
# If you use a custom roles_data file, edit the custom roles_data file and set the HostnameFormatDefault parameter for the Compute role:
# - name: Compute
#  ...
#  HostnameFormatDefault: '%stackname%-compute-%index%'
#  ...
# If you use the default roles_data file in openstack-tripleo-heat-templates, set the naming format in an environment file. Edit the environment file with your node counts and flavors, which is usually named node-info.yaml. Add the ComputeHostnameFormat parameter to the parameter_defaults section:
# parameter_defaults:
#  ...
#  ComputeHostnameFormat: '%stackname%-compute-%index%'
#  ...
