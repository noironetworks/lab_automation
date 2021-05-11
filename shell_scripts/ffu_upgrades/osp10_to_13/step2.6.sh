############################################################################
# 2.6. UPDATING THE CURRENT OVERCLOUD PACKAGES FOR OPENSTACK PLATFORM 10.Z
############################################################################

# 1. Check your subscription management configuration for the rhel_reg_release parameter.
#    If this parameter is not set, you must include it and set it version 7.7
# 1.5 copy the file from:
#  /usr/share/openstack-tripleo-heat-templates/extraconfig/pre_deploy/rhel-registration/environment-rhel-registration.yaml
#     to the templates directory, and edit it to add the "7.7" for rhel_reg_release.
cp /usr/share/openstack-tripleo-heat-templates/extraconfig/pre_deploy/rhel-registration/environment-rhel-registration.yaml /home/stack/templates
# 1.6 Subscribe the requisite RHEL7 repos to support OVS (needed on all the overcloud nodes with OVS):
sudo subscription-manager repos --enable=rhel-7-server-extras-rpms
sudo subscription-manager repos --enable=rhel-7-server-optional-rpms
# 2. Update the current plan using your original openstack overcloud deploy command and
#    including the --update-plan-only option
cat > install_cmd_plan_only << EOL
openstack overcloud deploy \
    --update-plan-only \
    --templates \
    -e /usr/share/openstack-tripleo-heat-templates/environments/network-isolation.yaml \
    -e /home/stack/templates/network-environment.yaml \
    -e /home/stack/templates/environment-rhel-registration.yaml \\
    -e /home/stack/templates/ciscoaci-config.yaml \
    -e /home/stack/templates/sauto.yaml \
    --ntp-server 172.28.184.8 \
    --control-flavor control \
    --compute-flavor compute
EOL
chmod +x install_cmd_plan_only
./install_cmd_plan_only
# 3. Create a static inventory file of your overcloud
# 4. Create a playbook that contains a task to set the operating system version to Red Hat
#    Enterprise Linux 7.7 on all nodes
# 5. Run the set_release.yaml playbook
# 6. Perform a package update on all nodes using the openstack overcloud update command
openstack overcloud update stack -i overcloud
# 7. The update process starts. During this process, the director reports an IN_PROGRESS status
#    and periodically prompts you to clear breakpoints.
# 8. The script automatically predefines the update order of nodes
# 9. The update command reports a COMPLETE status when the update completes
# 10. If you configured fencing for your Controller nodes, the update process might disable it.
#     When the update process completes, re-enable fencing with the following command on one of the
#     Controller nodes
sudo pcs property set stonith-enabled=true
