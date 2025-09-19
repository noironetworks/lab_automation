This directory contains ansible playbooks to perform the adoption process
of Red Hat OpenStack Platform (OSP) Director version 17.1 (stable/wallaby) for
Red Hat OpenStack Services on OpenShift (RHOSO) 18 (stable/2023.1). The playbooks
are numbered to match the steps in the Red Hat Documentation for the OSP 17 => RHOSO 18
adoption process. However, the actual playbooks are specific to deploys using
the in-house automation and deployment for our FABs.

The playbooks are run from the undercloud VM, but require running commands on the
provisioning node of the OpenShift cluster used for the RHOSO 18 control plane. In
order to run ansible playbooks on the provisioning node, you must first set up
passwordless SSH from the undercloud node. In addition, some of the playbooks
require running shell scripts from the provisioning node that ssh ing into the
RHOSP17.1 overcloud nodes. To allow this, the public key from the provisioning
node must be installed onto the overcloud nodes.

In the examples below, the playbooks are run from the /home/stack/ffu directory on
the undercloud host.

The upgrade process presumes that the same undercloud subnets will be reused (i.e. no
new subnet for the new OpenShift cluster and OpenStack control plane).

There are two places that may require hand edits before running, both in the step5.2.yaml
playbook. The first is in step 8, which does a string literal for creating the secret for
registry logins (I couldn't figure out a way to keep the JSON dictionary formatting and
encode the secret in a play - maybe someone can use AI to figure this out).
If you need a different set of credentials for registry logins, then change those here.
The second is in the NIC templates embedded in step 9. You should use the templates/nic-configs/compute.yaml
as the basis for what you use here.

# Upgrade process

The process starts with a session on the undercloud node.

1. ssh into each of the RHOSP17.1 overcloud nodes, to add them to the undercloud's known_hosts  file.
<pre><code>$ source ~/stackrc
$ for server in $(metalsmith list | grep overcloud | awk -F"=" '{print $2}' | awk \
'{print $1}'); do ssh tripleo-admin@$server "ls"; done
</code></pre>

2. Set up passwordless-SSH with the RHOSO 18 provisioning node, for running ansible playbooks.

Add the undercloud's public SSH key to the RHOSO provisioning node for passwordless-ssh
<pre><code>$ ssh-copy-id -i /home/stack/.ssh/id_rsa.pub noiro@i < provisioning node IP or DNS name >
</code></pre>

For example:
<pre><code>$ ssh-copy-id -i /home/stack/.ssh/id_rsa.pub noiro@172.22.172.215
</code></pre>

Note: you'll need to enter the password for that user on the provisioning node.

Verify that passwordless ssh into the RHOSO 18 provisioning node now works. Using the provisioning node IP from the example above:
<pre><code>$ ssh noiro@172.22.172.215
</code></pre>

3. Create a new ansible inventory file from the RHOSP 17.1 file, including the RHOSO provisioning node.

Some of the playbooks use the RHOSP 18 provisioning node as a host, so it must be added to the ansible inventory file.
Here's an example of how to create the combined RHOSP 17.1 and RHOSO 18 ansible inventory file:

<pre><code>$ cp /home/stack/overcloud-deploy/overcloud/tripleo-ansible-inventory.yaml /home/stack/ffu/ffu-inventory.yaml
$ cat << EOF >> /home/stack/ffu/ffu-inventory.yaml
Rhoso18:
  hosts:
    rhoso_provisioning:
      ansible_host: 172.22.172.215
      ansible_ssh_user: noiro
EOF
</code></pre>

4. Set up passwordless SSH from the provisioning node to the RHOSP 17.1 overcloud controller1

Some of the playbooks use the provisioning node as a host to run shell scripts, and some of the shell scripts run
ssh commands to the RHOSP 17.1 overcloud controller1. To allow this, the provisoining node's public SSH key needs
to be added to the RHOSP 17.1 overcloud controller 1 host.

The following playbooks get the public key from the RHOSO 18 provisioniong node, and append it to
the authorized_keys files on the overcloud controller hosts.

<pre><code>$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step0.1.yaml
$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step0.2.yaml
</code></pre>

Do an ssh into the overcloud controller public IPs, as well as all the overcloud
controlplane IPs:

<pre><code>$ ssh tripleo-admin@172.22.172.211
$ ssh tripleo-admin@1.100.1.51
</code></pre>


5. Set up the proxy configuration on the computes
<pre><code>$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml change_proxy.yaml
</code></pre>

6. Run the playbook to ensure that all nodes have valid Red Hat Subscriptions:

<pre><code>$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step0.yaml
</code></pre>

7. Run the playbook to ensure that sytemd-container is installed on all the compute hosts:

<pre><code>$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step1.5.yaml
</code></pre>

8. Run playbook to extract information for the undercloud networks

<pre><code>$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step1.7.0.yaml
$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step1.7.1.yaml
</code></pre>

9. Run the playbooks to generate the YAML files needed by RHOSO-18 for the undercloud networks

<pre><code>$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step1.7.3.1.yaml
$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step1.7.3.2.yaml
$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step1.7.3.3.yaml
</code></pre>

10. Run the playbook to apply the CRs created from section 1.7

<pre><code>$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step1.7.4.yaml
</code></pre>

Note: the above playbook is not idempotent. If there are any failures, the CRs that were created must first be deleted
before the playbook can be re-run.

11. Run the playbook to install the os-diff tool on the provisioning node

<pre><code>$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step1.10.yaml
</code></pre>

12. Run the playbooks for adopting the DB

<pre><code>$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step3.1-1.yaml
$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step3.1-2.yaml
$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step3.2.yaml
$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step3.4-1.yaml
$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step3.4-2.yaml
</code></pre>

The last step of 3.4 requires manually logging in to the provisioning node and runniong
the shell script created by step3.4-2.yaml:
<pre><code>$ sh ./disable-services.sh
</code></pre>

Finish by running the DB adoption playbooks:
<pre><code>$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step3.5-1.yaml
$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step3.5-2.yaml
</code></pre>

Note: when I ran these, I had to change the db_en_vars.sh file to use the private mariadb IPs,
as haproxy was saying that the backend servers were down (even though they weren't).

13. Adopt the OpenStack control plane services

Run the playbooks to adopt the OpenStack control plane services into the RHOSO 18 OCP cluster:

<pre><code>$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step4.1.yaml
$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step4.4.yaml
$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step4.5.yaml
$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step4.6.yaml
$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step4.7.yaml
$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step4.9.yaml
$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step4.10.yaml
$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step4.11.yaml
$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step4.13.yaml
$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step4.18-1.yaml
$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step4.18-2.yaml
</code></pre>

14. Adopt the OpenStack data plane

Note that the registry login credentials are hard-coded in step5.2.yaml. If for some
reason you need to use different credentials, just edit the values in step 8 of that
playbook.

Run the playbooks to adopt the OpenStack data plane into the RHOSO 18 OCP cluster:

<pre><code>$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step5.1.yaml
$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step5.2.yaml
</code></pre>

The step5.2.yaml playbook takes a while to complete. The deployment that gets
is the last CR to complete reconciliation. You can monitor its progress using
this command:

<pre><code>$ oc get openstackdataplanedeployments
NAME                     NODESETS              STATUS   MESSAGE
openstack                ["openstack-cell1"]   False    Deployment in progress
openstack-pre-adoption   ["openstack-cell1"]   True     Setup complete
tripleo-cleanup          ["openstack-cell1"]   True     Setup complete
</code></pre>

Once the openstack deployment on openstack-cell1 completes, you can continue
running the playbooks.

<pre><code>$ ansible-playbook -i /home/stack/ffu/ffu-inventory.yaml step5.3.yaml
</code></pre>
