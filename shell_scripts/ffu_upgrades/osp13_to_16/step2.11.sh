############################################################################
# 2.11. Validating Red Hat OpenStack Platform 13 before the upgrade
############################################################################
# 1. Log in to the undercloud as the stack user.
# 2. Source the stackrc file:
source ~/stackrc
# 3. Create a bash script called pre-upgrade-validations.sh and include the following content in the script:
cat > pre-upgrade-validations.sh << EOL
#!/bin/bash
for VALIDATION in $(openstack action execution run tripleo.validations.list_validations '{"groups": ["pre-upgrade"]}' | jq ".result[] | .id")
do
  echo "=== Running validation: $VALIDATION ==="
  STACK_NAME=$(openstack stack list -f value -c 'Stack Name')
  ID=$(openstack workflow execution create -f value -c ID tripleo.validations.v1.run_validation "{\"validation_name\": $VALIDATION, \"plan\": \"$STACK_NAME\"}")
  while [ $(openstack workflow execution show $ID -f value -c State) == "RUNNING" ]
  do
    sleep 1
  done
  echo ""
  openstack workflow execution output show $ID | jq -r ".stdout"
  echo ""
done
EOL
# 4. Add permission to run the script:
chmod +x pre-upgrade-validations.sh
# 5. Run the script:
./pre-upgrade-validations.sh

