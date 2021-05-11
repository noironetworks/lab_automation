############################################################################
# 8.1 Creating an upgrades environment file
############################################################################
# 1. Log in to the undercloud as the stack user.
# 2. Create an environment file called upgrades-environment.yaml in your templates directory:
touch /home/stack/templates/upgrades-environment.yaml
# 3. Edit the file and add the following mandatory content:
cat > /home/stack/templates/upgrades-environment.yaml << EOL
parameter_defaults:
  DnfStreams: [{'module':'container-tools', 'stream':'2.0'}]
  UpgradeInitCommand: |
    {% if 'Compute' in group_names or 'Controller' in group_names %}
    sudo dnf module disable -y virt:rhel
    sudo dnf module enable -y virt:8.2
    {% endif %}
  UpgradeLeappCommandOptions: >-
    {%- if 'Compute' in group_names or 'Controller' in group_names %}
    --enablerepo rhel-8-for-x86_64-baseos-eus-rpms
    --enablerepo rhel-8-for-x86_64-appstream-eus-rpms
    --enablerepo fast-datapath-for-rhel-8-x86_64-rpms
    {%- else %}
    --enablerepo rhel-8-for-x86_64-baseos-rpms
    --enablerepo rhel-8-for-x86_64-appstream-rpms
    {%- endif %}
EOL
# 4. Save the upgrades-environment.yaml file.
