############################################################################
# 14.1 Updating network interface templates
############################################################################
# 1. Log in to the undercloud as the stack user.
# 2. Source the stackrc file.
source ~/stackrc
# 3. On the undercloud, create a file called update-nic-templates.sh and include the following content in the file:
cat > update-nic-templates.sh << EOL
#!/bin/bash
STACK_NAME="overcloud"
ROLES_DATA="/home/stack/templates/custom_roles_data.yaml"
NETWORK_DATA="/usr/share/openstack-tripleo-heat-templates/network_data.yaml"
NIC_CONFIG_LINES=\$(openstack stack environment show \$STACK_NAME | grep "::Net::SoftwareConfig" | sed -E 's/ *OS::TripleO::// ; s/::Net::SoftwareConfig:// ; s/ http.*user-files/ /')
echo "\$NIC_CONFIG_LINES" | while read LINE; do
    ROLE=\$(echo "\$LINE" | awk '{print \$1;}')
    NIC_CONFIG=\$(echo "\$LINE" | awk '{print \$2;}')

    if [ -f "\$NIC_CONFIG" ]; then
        echo "Updating template for \$ROLE role."
        python3 /usr/share/openstack-tripleo-heat-templates/tools/merge-new-params-nic-config-script.py \
            --tht-dir /usr/share/openstack-tripleo-heat-templates \
            --roles-data \$ROLES_DATA \
            --network-data \$NETWORK_DATA \
            --role-name "\$ROLE" \
            --discard-comments yes \
            --template "\$NIC_CONFIG"
    else
        echo "No NIC template detected for \$ROLE role. Skipping \$ROLE role."
    fi
done
EOL
# If you use a custom overcloud name, Set the STACK_NAME variable to the name of your overcloud. The default name for an overcloud stack is overcloud.
# If you use a custom roles_data file, set the ROLES_DATA variable to the location of the custom file. If you use the default roles_data file, leave the variable as /usr/share/openstack-tripleo-heat-templates/roles_data.yaml
# If you use a custom network_data file, set the NETWORK_DATA variable to the location of the custom file. If you use the default network_data file, leave the variable as /usr/share/openstack-tripleo-heat-templates/network_data.yaml
# Run /usr/share/openstack-tripleo-heat-templates/tools/merge-new-params-nic-config-script.py -h to see a list of options to add to the script.
# 4. Add executable permissions to the script:
chmod +x update-nic-templates.sh
# 5. Run the script:
./update-nic-templates.sh

