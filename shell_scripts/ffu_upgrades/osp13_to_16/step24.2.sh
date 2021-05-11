############################################################################
# 24.2 Validating the post-upgrade functionality
############################################################################
# 1. Source the stackrc file.
source ~/stackrc
# 1.1 Use setenforce 0 on all controllers, to fix problems with glance: 
for server in $(nova list | awk -F"=" /overcloud/'{print $2}' | cut -d" " -f 1); do ssh heat-admin@$server "sudo setenforce 0"; done
# 2. Run the openstack tripleo validator run command with the --group post-upgrade option:
openstack tripleo validator run --group post-upgrade
# 3. Review the results of the validation report. To view detailed output from a specific validation, run the openstack tripleo validator show run command against the UUID of the specific validation from the report:
openstack tripleo validator show run <UUID>
