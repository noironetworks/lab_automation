This directory contains ansible playbooks to perform a minor update for
Red Hat OpenStack Platform (OSP) Director version 17.1 (stable/wallaby). The
playbooks are numbered to match the steps in the Red Hat Documentation for
OSP17.1 minor updates. However, the actual playbooks are specific to upgrades
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
1. ssh into each of the overcloud nodes, to add them to the undercloud's known_hosts file.

<pre><code>$ for server in $(metalsmith -c "IP Addresses" -f value list | awk \
-F"=" '{print $2}'); do ssh tripleo-admin@$server "ls"; done
</code></pre>

2. Run the playbook to fix NAT on the undercloud host/VM:
<pre><code>$ ansible-playbook -i /home/stack/overcloud-deploy/overcloud/tripleo-ansible-inventory.yaml fix-nat.yaml
</code></pre>

3. Run the playbook to ensure that all nodes have valid Red Hat Subscriptions:
<pre><code>$ ansible-playbook -i /home/stack/overcloud-deploy/overcloud/tripleo-ansible-inventory.yaml step0.yaml
</code></pre>

4. Run playbook to update Red Hat Subscription Manager (RHSM) parameters:

<pre><code>$ ansible-playbook -i /home/stack/overcloud-deploy/overcloud/tripleo-ansible-inventory.yaml step1.3.yaml
</code></pre>

5. Run the set_release.yaml to lock all nodes to the 9.2 RHEL release:

<pre><code>$ $ ansible-playbook -i /home/stack/overcloud-deploy/overcloud/tripleo-ansible-inventory.yaml -f 25 ./set_release.yaml --limit undercloud,Controller,Compute
</code></pre>

6. Run playbook to update the RHSM parameters to include the EUS repos:

<pre><code>$ ansible-playbook -i /home/stack/overcloud-deploy/overcloud/tripleo-ansible-inventory.yaml step1.4.yaml
</code></pre>

7. Run the update_rhosp_repos.yaml playbook:

<pre><code>$ ansible-playbook -i /home/stack/overcloud-deploy/overcloud/tripleo-ansible-inventory.yaml -f 25 ./update_rhosp_repos.yaml --limit undercloud,Controller,Compute
</code></pre>

8. Continue with the playbooks
<pre><code>$ ansible-playbook -i /home/stack/overcloud-deploy/overcloud/tripleo-ansible-inventory.yaml step1.5.yaml
$ ansible-playbook -i /home/stack/overcloud-deploy/overcloud/tripleo-ansible-inventory.yaml step1.6.yaml
$ ansible-playbook -i /home/stack/overcloud-deploy/overcloud/tripleo-ansible-inventory.yaml step2.1.yaml
</code></pre>

9. Rotate your keys to get the correct key length/size
<pre><code>$ ansible-playbook -i /home/stack/overcloud-deploy/overcloud/tripleo-ansible-inventory.yaml \
    -e undercloud_backup_folder=/home/stack/overcloud_backup_keys \
    -e stack_name=overcloud \ /usr/share/ansible/tripleo-playbooks/ssh_key_rotation.yaml
</code></pre>

10. Run the playbook to update the undercloud
<pre><code>$ ansible-playbook -i /home/stack/overcloud-deploy/overcloud/tripleo-ansible-inventory.yaml step2.3.yaml
</code></pre>

That last step reboots the undercloud.

11. Log in to the undercloud and continue with the playbooks:
<pre><code>$ source ~/stackrc
$ ansible-playbook -i /home/stack/overcloud-deploy/overcloud/tripleo-ansible-inventory.yaml step2.4.yaml
</code></pre>

12. Install new Cisco Tripleo RPM and build the Cisco containers:
<pre><code>$ ansible-playbook -i /home/stack/overcloud-deploy/overcloud/tripleo-ansible-inventory.yaml step2.5.yaml
</code></pre>

13. Continue running the ansible playbooks:
<pre><code>$ ansible-playbook -i /home/stack/overcloud-deploy/overcloud/tripleo-ansible-inventory.yaml step3.1.yaml
$ ansible-playbook -i /home/stack/overcloud-deploy/overcloud/tripleo-ansible-inventory.yaml step3.2.yaml
$ ansible-playbook -i /home/stack/overcloud-deploy/overcloud/tripleo-ansible-inventory.yaml step3.5.yaml
$ ansible-playbook -i /home/stack/overcloud-deploy/overcloud/tripleo-ansible-inventory.yaml step3.7.yaml
$ ansible-playbook -i /home/stack/overcloud-deploy/overcloud/tripleo-ansible-inventory.yaml step3.13.yaml
$ ansible-playbook -i /home/stack/overcloud-deploy/overcloud/tripleo-ansible-inventory.yaml step3.14.yaml
</code></pre>

14. Reboot the overcloud nodes:

At this point, all the nodes have been upgraded, but may need to be rebooted before certain
software/packages updates can take effect (e.g. openvswitch). Reboot controller nodes one
by one, but make sure you always have at least 2 controller nodes fully up at any given
moment, in order to ensure that the pacemaker cluster is intact (multi-controller installations
only). For compute nodes, be sure to evacuate the instances from the compute host before
rebooting it.
