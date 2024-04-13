This directory contains code for creating arbitrary scale in an OpenStack
cloud.

# Ansible
The ansible playbooks are used for making REST calls to ACI. We've chosen
to only use the bare REST module, instead of the resource-specific ansible
modules, in order to allow for better compatibility, since all ansible
versions should at least support the raw REST module for ACI.

# Limitations
Simulation may result in differences from the desired configuration.
FOr example, in order to simulate the required number of agents connected
to the fabric, multiple agents must be presented on the same switch port.
This triggers the use of remote endpoints, while the system being emulated
would not use remote endpoints.

This should be used with https://github.com/noironetworks/load-testing

The scale.py
code creates terraform scripts to create infrastructure. The terraform
scripts creates a canned configuration per project in OpenStack. The
python scripts creates a per-project directory, and instantiates a
terraform script to create the resources for that project.

Once the terraform scripts have been applied, another script is needed
to create the ports on the OVS bridges. The ports.py code creates shell
scripts that must be uploaded to compute hosts and executed, so that the
virtual interfaces can be created and attached to the OVS bridges. This
will cause the neutron-opflex-agent to request port details and create
EP files.

The shell script in this repo does checks to make sure that the right
software is installed.
The ansible playbooks require the APIC host info. This is specified in
an anisble variable defined in the playbook, which can also be overriden
when invoking the ansible-playbook command.
<pre><code>$ cat /tmp/apic_info.yaml
apic_ip: 10.30.120.190
apic_username: admin
apic_password: noir0123
</code></pre>

The contents of the contract_info.yaml file:
<pre><code>$ cat /tmp/contract_info.yaml
filter_dn_name: "default"
filter_namealias: ""
vzentry_dn_name: "default"
vzentry_namealias: ""
contract_dn_name: "PROVIDE-PCF_CON"
contract_namealias: ""
subject_dn_name: "PROVIDE-PCF_SBJ"
subject_namealias: ""
filter_dn_name: "default"
filter_namealias: ""
</code></pre>

# Sample commands:
1. Help for scale.py

<pre><code>$ python scale.py -h
usage: scale.py [-h] [--cloud-ip CLOUD_IP] [--tenant-count TENANT_COUNT]
                [--tenant-prefix TENANT_PREFIX] [--simulated-ports]

Scale test manager

optional arguments:
  -h, --help            show this help message and exit
  --cloud-ip CLOUD_IP   IP Address of OpenStack horizon.
  --tenant-count TENANT_COUNT
                        Number of tenants to create resources in.
  --tenant-prefix TENANT_PREFIX
                        Tenant name prefix
  --simulated-ports     Create simulated VMs (i.e. bound ports only).
</code></pre>

2. Sample scale.py command:

<pre><code>$ python scale.py --cloud-ip 10.30.120.201 --tenant-count 3 --tenant-prefix prj --simulated-ports
Making directory /home/noiro/test/prj0
Making directory /home/noiro/test/prj1
Making directory /home/noiro/test/prj2
</code></pre>

3. Go in to the per-project directory and apply the terraform scripts:

<pre><code>$ cd /home/noiro/test/prj0
$ terraform init
....
$ terraform plan
....
$ terraform apply -auto-approve
</code></pre>

4. Help for ports.py

<pre><code>$ python ports.py -h
usage: ports.py [-h] [--cloud-ip CLOUD_IP] [--tenant TENANT]
                [--port-filter PORT_FILTER] [--simulated-ports]

Port manager

optional arguments:
  -h, --help            show this help message and exit
  --cloud-ip CLOUD_IP   IP Address of OpenStack horizon.
  --tenant TENANT       Tenant name or UUID
  --port-filter PORT_FILTER
                        Additional string to use for port filtering
  --simulated-ports     Create simulated VMs (i.e. bound ports only).
</code></pre>

5. Sample create port scripts:

<pre><code>$ python ports.py --cloud-ip 10.30.120.201 --tenant admin --simulated-ports

</code></pre>

6. Run the shell scripts on the compute host

<pre><code>$ 
</code></pre>

