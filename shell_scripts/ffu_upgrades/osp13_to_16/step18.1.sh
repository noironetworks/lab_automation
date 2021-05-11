############################################################################
# 18.1 Running the overcloud upgrade preparation
############################################################################
# 0.1 remove the old openstack-tripleo-heat-templates directory in /home/stack:
rm -rf openstack-tripleo-heat-templates
# 0.2 Copy over the templates directory into /home/stack:
cd /home/stack
cp -r /usr/share/openstack-tripleo-heat-templates  tripleo-heat-templates
# 1. Source the stackrc file:
source ~/stackrc
# 2. Run the upgrade preparation command:
cat > upgrade_prepare.sh << EOL
openstack overcloud upgrade prepare \
    --templates /home/stack/tripleo-heat-templates \
    -r /home/stack/templates/custom_roles_data.yaml \
    -e /home/stack/templates/upgrades-environment.yaml \
    -e /home/stack/templates/rhsm.yaml \
    -e /home/stack/templates/containers-prepare-parameter.yaml \
    -e /home/stack/tripleo-heat-templates/environments/network-isolation.yaml \
    -e /home/stack/templates/network-environment.yaml \
    -e /home/stack/templates/ciscoaci_containers.yaml \
    -e /home/stack/templates/ciscoaci_containers_stein.yaml \
    -e /home/stack/templates/ciscoaci-config.yaml
EOL
# 2.1 Make it executable:
chmod +x ./upgrade_prepare.sh
# 2.2 Run the upgrade prepare:
./upgrade_prepare.sh
# 3. Wait until the upgrade preparation completes.
# 4. Download the container images:
openstack overcloud external-upgrade run --stack overcloud --tags container_image_prepare
