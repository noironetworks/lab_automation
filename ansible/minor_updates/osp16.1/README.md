This directory contains ansible playbooks to perform a minor update for
Red Hat OpenStack Platform (OSP) Director version 16 (stable/train). The
playbooks are numbered to match the steps in the Red Hat Documentation for
OSP16 minor updates. However, the actual playbooks are specific to upgrades
using the automation for our FABs.

The playbooks should be copied to and run from the undercloud. The playbooks require
that the latest OSP16 tripleo package and tarball are copied to the undercloud.

The playbooks should run, but I have seen some failures. For example, when a playbook
that reboots the undercloud is run, I've seen it not actually reboot it, and fail
the playbook (there usually is always an error message when running a task that has
a reboot task, since the task can't report back due to the reboot, but the reboot
itself almost always works). The playbooks are largely idempotent, so you can run
one again if it fails.

# Upgrade process
1. Obtain the cloud inventory for ansible. Run this from the /home/stack directory:

<pre><code>$ source stackrc
$ ./get-overcloud-inventory.sh inventory.txt
</code></pre>

2. ssh into each of the overcloud nodes, to add them to the undercloud's known_hosts file.

<pre><code>$ for server in $(openstack server list -c Networks -f value | awk \
-F"=" '{print $2}'); do ssh heat-admin@$server "ls"; done
</code></pre>

3. Run the playbook to ensure that all nodes have valid Red Hat Subscriptions:

<pre><code>$ ansible-playbook -i inventory.txt step0.yaml
</code></pre>

4. Run playbook to update Red Hat Subscription Manager (RHSM) parameters:

<pre><code>$ ansible-playbook -i inventory.txt step2.1.yaml
</code></pre>

5. Create a static inventory file of your overcloud:

<pre><code>$ tripleo-ansible-inventory --ansible_ssh_user heat-admin --static-yaml-inventory ~/inventory.yaml
</code></pre>

6. Run the playbook to set the release:

<pre><code>$ ansible-playbook -i ~/inventory.yaml -f 25 ~/set_release.yaml --limit undercloud,Controller,Compute
</code></pre>

7. Run playbook to update the RHSM parameters to include the EUS repos:

<pre><code>$ ansible-playbook -i inventory.txt step2.2.yaml
</code></pre>

8. Run the change_tus playbook:

<pre><code>$ ansible-playbook -i ~/inventory.yaml -f 25 ~/change_tus.yaml --limit undercloud,Controller,Compute
</code></pre>

9. Run the change_eus.yaml playbook:

<pre><code>$ ansible-playbook -i ~/inventory.yaml -f 25 ~/change_eus.yaml --limit undercloud,Controller,Compute
</code></pre>

10. Run the update_rhosp_repos.yaml playbook:

<pre><code>$ ansible-playbook -i ~/inventory.yaml -f 25 ~/update_rhosp_repos.yaml --limit undercloud,Controller,Compute
</code></pre>

11. Run the update_ceph_repos.yaml playbook:

<pre><code>$ ansible-playbook -i ~/inventory.yaml -f 25 ~/update_ceph_repos.yaml --limit CephStorage
</code></pre>

12. Run the container-tools.yaml playbook against all nodes:

<pre><code>$ ansible-playbook -i ~/inventory.yaml -f 25 ~/container-tools.yaml
</code></pre>

13. Continue with the playbooks
<pre><code>$ ansible-playbook -i inventory.yaml step2.5.yaml
$ ansible-playbook -i inventory.txt step2.7.yaml
$ ansible-playbook -i inventory.txt step3.1.yaml
</code></pre>

That last step reboots the undercloud.

14. Log in to the undercloud and continue with the playbooks:
<pre><code>$ source ~/stackrc
$ ansible-playbook -i inventory.txt step3.2.yaml
</code></pre>

15. Install new Cisco Tripleo RPM and build the Cisco containers:
<pre><code>$ ansible-playbook -i inventory.txt step3.3.yaml
</code></pre>

16. If you are upgrading from the 5.1(3.20210217) release or older, you will need to run an
additional playbook to split the opflex agents/services into their own containers (they were
in the same container in these older releases):
<pre><code>$ ansible-playbook -i inventory.txt step4.0.yaml
</code></pre>

17. Continue running the ansible playbooks:
<pre><code>$ ansible-playbook -i inventory.txt step4.1.yaml
$ ansible-playbook -i inventory.txt step4.2.yaml
$ ansible-playbook -i inventory.txt step4.4.yaml
$ ansible-playbook -i inventory.txt step4.5.yaml
$ ansible-playbook -i inventory.txt step4.8.yaml
$ ansible-playbook -i inventory.txt step4.9.yaml
$ ansible-playbook -i inventory.txt step5.1.yaml
</code></pre>

18. Reboot the overcloud nodes:

At this point, all the nodes have been upgraded, but may need to be rebooted before certain
software/packages updates can take effect (e.g. openvswitch). Reboot controller nodes one
by one, but make sure you always have at least 2 controller nodes fully up at any given
moment, in order to ensure that the pacemaker cluster is intact (multi-controller installations
only). For compute nodes, be sure to evacuate the instances from the compute host before
rebooting it.
