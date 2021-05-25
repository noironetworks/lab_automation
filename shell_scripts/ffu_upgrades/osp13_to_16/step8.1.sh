############################################################################
# 8.1 Creating an upgrades environment file
############################################################################
# 1. Log in to the undercloud as the stack user.
# 2. Create an environment file called upgrades-environment.yaml in your templates directory:
#touch /home/stack/templates/upgrades-environment.yaml
# 3. Edit the file and add the following mandatory content:
cat > /home/stack/templates/upgrades-environment.yaml << EOL
parameter_defaults:
  UpgradeLeappDevelSkip: "LEAPP_UNSUPPORTED=1 LEAPP_DEVEL_TARGET_RELEASE=8.2"
  LeappInitCommand: |
    module=floppy; sudo lsmod | grep -q $module && { sudo rmmod $module; echo "$module unloaded"; } || echo "$module was not loaded"
    module=pata_acpi; sudo lsmod | grep -q $module && { sudo rmmod $module; echo "$module unloaded"; } || echo "$module was not loaded"
EOL
# 4. Save the upgrades-environment.yaml file.
