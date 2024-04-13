# Specific Scale Testing

This directory contains scripts that can be used to reproduce a simulated
version of configured scale in a specific OpenStack environment, when
the APIC AIM mechanism driver is used. The scripts create per-project
terraform scripts, which allows the specific scale to be added and
tested incrementally.

Although the scripts should be runable from any host that has openstack
python client access to the host, the workflow is easiest when run from
an undercloud (e.g. Red Hat OpenStack Platform Director node/host).

The following information must be collected from an OpenStack cloud:
* the configured and monitored AIM hash trees
* a dump of the ports in neutron
* a dump of the security groups in neutron
* a dump of the floating IPs in neutron

The scripts also need a file containing the list of compute hosts where the
simulated scale will be deployed.

In addition, due to limitations in the OpenStack Terraform provider [0], not
all resources can be created using terraform scripts.

# Collecting AIM JSON hash trees
To collect the AIM hash trees, run the following commands on an OpenStack
controller (i.e. where the AIM service is running):
<pre><code>$ podman exec -it ciscoaci_aim aimctl hashtree dump > config_hahtrees.json
podman exec -it ciscoaci_aim aimctl hashtree dump -f monitored > monitored_trees.json
</code></pre>

The format of this output is human-readable JSON data, but needs to be fxied in order
for it to be consumed as a JSON file for the scripts. This step is unfortunately
manual (feature request for AIM: dump trees in JSON-parsable file format).

# Collecting port JSON data
Run the following command from any place that can run the OpenStack python client
commands to the cloud:
<pre><code>$ openstack port list -f json > ports.json
</code></pre>

# Collecting security group rules JSON data
Run the following command from any place that can run the OpenStack python client
commands to the cloud:
<pre><code>$ openstack security group rule list -f json > sg_rules.json
</code></pre>

# Collecting flaoting IPs JSON data
Run the following command from any place that can run the OpenStack python client
commands to the cloud:
<pre><code>$ openstack floating ip list -f json > fips.json
</code></pre>

# Creating the hosts file
Run the following command from any place that can run the OpenStack python client
commands to the cloud:
<pre><code>$ openstack network agent list -c Host -f value | grep compute | sort | uniq
</code></pre>

The inventory can then be edited as per testing requirements.

# Run the Terraform script generator
The trees_to_tf.py script takes the input data collected from the previous steps,
along with the IP and credentials for the cloud, and creates a directory per OpenStack
project that contains a terraform script to create all the resources for that project.

1. Help for trees_to_tf.py

<pre><code>$ python trees_to_tf.py -h
usage: trees_to_tf.py [-h] [--cloud-ip CLOUD_IP] [--cloud-user CLOUD_USER]
                      [--cloud-password CLOUD_PASSWORD]
                      [--config-tree-file CONFIG_TREE_FILE]
                      [--monitor-tree-file MONITOR_TREE_FILE]
                      [--ports-file PORTS_FILE]
                      [--security-groups-file SECURITY_GROUPS_FILE]

OpenStack Terraform Configuration Generator

optional arguments:
  -h, --help            show this help message and exit
  --cloud-ip CLOUD_IP   IP Address of OpenStack horizon.
  --cloud-user CLOUD_USER
                        User of the OpenStack cloud
  --cloud-password CLOUD_PASSWORD
                        Password for theUser of the OpenSTack cloud
  --config-tree-file CONFIG_TREE_FILE
                        Full path to the configured state hashtree file
  --monitor-tree-file MONITOR_TREE_FILE
                        Full path to the monitored state hashtree file
  --ports-file PORTS_FILE
                        Full path to the file containing the ports in
                        OpenStack
  --security-groups-file SECURITY_GROUPS_FILE
                        Full path to the file with security group data in
                        OpenStack
</code></pre>

2. Example command for trees_to_tf.py

Here's an example of the command:
<pre><code>$ python trees_to_tf.py --cloud-ip 10.30.120.201 --cloud-user admin --cloud-password noir0123 --config-tree-file ctrees.json --monitor-tree-file montrees.
json --security-groups-file sg_rules.json  --ports-file port.json
Making directory /home/noiro/test/testing/prj_00bb6a67fa6a49afbd45b6d6c477ccf2
Making directory /home/noiro/test/testing/prj_012455f90ba6413c87a8d6e084a76536
Making directory /home/noiro/test/testing/prj_0155d609dd2e4b458cdc46f38afbdbba
Making directory /home/noiro/test/testing/prj_01f43b55dfc34bbeaab15c69a4ea456b
....
</code></pre>

# Run the port binding and OVS script generator
Once the terraform scripts have been generated, another script is needed
to create the ports on the OVS bridges. The ports.py code creates two different
types of shell scripts:
* per-host shell scripts to create and delete ports on the OVS bridge for the
  project
* a shell script that can be used to bind the ports to those hosts

The OVS shell scripts are then uploaded to the respsective compute hosts and executed,
so that the virtual interfaces can be created and attached to the OVS bridges. This
causes the neutron-opflex-agent to request the port details and create EP files.

3. Sample create port scripts:
<pre><code>$ python ports.py --ports-file port.json --tenant 50dbb2f6fb08436d906f58aaee3996b0 --hosts-file hosts.txt --max-per-host 10
</code></pre>

4. Run the shell script to bind the ports to the compute hosts
Run the shell script to bind the ports. Make sure that you have sourced
the credentials for the overcloud before running it.

<pre><code>$  sh ./bind-ports.sh
</code></pre>

6. Run the shell scripts on the compute host
<pre><code>$ sh ./create-ports-<<hostname>>.sh
</code></pre>

This is an example of getting the create and delete commands needed to run with the terraform scripts:
<pre><code>$ for dir in $(ls | grep prj); do egrep -rI  'create command:' $dir | awk -F"command:" '{print $2}' | sort | uniq > create-commands.sh
$ for dir in $(ls | grep prj); do egrep -rI  'delete command:' $dir | awk -F"command:" '{print $2}' | sort | uniq > delete-commands.sh
</code></pre>


    [0] The OpenStack provider for Terraform doesn't support extensions to OpenStack
    resources. This means any resources that need things lik APIC DNs (e.g. OpenStack
    external networks) can't be creqated using terraform. In those cases, terraform's
    ability to use pre-existing resources is leveraged. This means these resources must
    be created outside of the scriptiong. Fortunately, the resources requiring extensions
    are typically for specific uses and small in number (e.g. external networks).
