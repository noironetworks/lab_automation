This directory contains ansible playbooks to perform a minor update for
Red Hat OpenStack Platform (OSP) Director version 13 (stable/queens). The
playbooks are numbered to match the steps in the Red Hat Documentation for
OSP13 minor updates. However, the actual playbooks are specific to upgrades
using the automation for our FABs.

The playbooks should be copied to and run from the undercloud. The playbooks require
that the latest OSP13 tripleo package and tarball are copied to the undercloud.

The playbooks should run, but I have seen some failures. For example, when a playbook
that reboots the undercloud is run, I've seen it not actually reboot it, and fail
the playbook (there usually is always an error message when running a task that has
a reboot task, since the task can't report back due to the reboot, but the reboot
itself almost always works). The playbooks are largely idempotent, so you can run
one again if it fails.

# Upgrade process
1. Obtain the cloud inventory for ansible. Run this from the /home/stack directory:

<pre><code>$ source stackrc
$ ./get-overcloud-inventory.sh inventory.yaml
</code></pre>

2. ssh into each of the overcloud nodes, to add them to the undercloud's known_hosts file.

<pre><code>$ for server in $(openstack server list -c Networks -f value | awk \
-F"=" '{print $2}'); do ssh heat-admin@$server "ls"; done
</code></pre>

3. Run the playbook to ensure that all nodes have valid Red Hat Subscriptions:

<pre><code>$ ansible-playbook -i inventory.yaml step0.yaml
</code></pre>

4. Continue with the playbooks
<pre><code>$ ansible-playbook -i inventory.yaml step2.5.yaml
$ ansible-playbook -i inventory.yaml step3.1.yaml
</code></pre>

That last step reboots the undercloud.

5. Log in to the undercloud and continue with the playbooks:
<pre><code>$ source ~/stackrc
$ ansible-playbook -i inventory.yaml step3.2.yaml
</code></pre>

6. Install new Cisco Tripleo RPM and build the Cisco containers:
<pre><code>$ ansible-playbook -i inventory.yaml step3.3.yaml
</code></pre>

7. If you are upgrading from the 5.1(3.20210217) release or older, you will need to run an
additional playbook to split the opflex agents/services into their own containers (they were
in the same container in these older releases):
<pre><code>$ ansible-playbook -i inventory.yaml step4.0.yaml
</code></pre>

8. Continue running the ansible playbooks:
<pre><code>$ ansible-playbook -i inventory.yaml step4.3.yaml
$ ansible-playbook -i inventory.yaml step4.4.yaml
$ ansible-playbook -i inventory.yaml step4.5.yaml
$ ansible-playbook -i inventory.yaml step4.8.yaml
$ ansible-playbook -i inventory.yaml step5.1.yaml
</code></pre>

9. Reboot the overcloud nodes:

At this point, all the nodes have been upgraded, but may need to be rebooted before certain
software/packages updates can take effect (e.g. openvswitch). Reboot controller nodes one
by one, but make sure you always have at least 2 controller nodes fully up at any given
moment, in order to ensure that the pacemaker cluster is intact (multi-controller installations
only). For compute nodes, be sure to evacuate the instances from the compute host before
rebooting it.
