This directory contains ansible playbooks to perform the In-Place Upgrade
from Red Hat OpenStack Platform (OSP) Director version 16.2 (stable/train) to
OSP17 (stable/wallaby). The playbooks are numbered to match the steps in the
Red Documentation for the OSP16 => OSP17 In-Place Upgrade process. However,
the actual playbooks are specific to deploys using our sauto automation for our FABs.

The playbooks should be copied and run from the undercloud VM. The playbooks require
that the OSP17 tripleo package and tarballs also be copied to the undercloud.

The playbooks should run, but I have seen some failures. For example, when a playbook
that reboots the undercloud VM is run, I've seen it not actually reboot it, and fail
the playbook (there usually is always an error message when running a task that has
a reboot task, since the task can't report back due to the reboot, but the reboot
itself almost always works). The playbooks are largely idempotent, so you can run
one again if it fails.

# Upgrade process

1. Obtain the cloud inventory for ansible. Run this from the /home/stack direcotory:
<pre><code>$ source stackrc
$ ./get-overcloud-inventory.sh inventory.yaml
</code></pre>

2. ssh into each of the overcloud nodes, to add them to the undercloud's known_hosts  file.
<pre><code>
$ for server in $(openstack server list -c Networks -f value | awk \
-F"=" '{print $2}'); do ssh heat-admin@$server "ls"; done
</code></pre>

3. Run the ansible playbook to remove the old ACI repo

<pre><code>$ ansible-playbook -i inventory.yaml remove_repo.yaml
</code></pre>

4. Run the ansible playbook to clean up subscriptions of all the nodes

<pre><code>$ ansible-playbook -i inventory.yaml step0.yaml
</code></pre>

5. Run the ansible playbooks to perform the upgrade of the undercloud

<pre><code>$ ansible-playbook -i inventory.yaml step2.1.yaml
$ ansible-playbook -i inventory.yaml step2.3.yaml
$ ansible-playbook -i inventory.yaml step2.5.yaml
$ ansible-playbook -i inventory.yaml step2.6.yaml
$ ansible-playbook -i inventory.yaml step2.8.yaml
</code></pre>

At this point, the RHOSP version of the undercloud should be upgraded (i.e. now RHOSP17).

6. Run the ansible playbooks to prepare for the overcloud adoption phase

<pre><code>$ ansible-playbook -i inventory.yaml step4.2.yaml
$ ansible-playbook -i inventory.yaml step4.4.yaml
</code></pre>

7. Run the step to install the new tripleo for ACI plugin RPM (OSP17 version), and build the RHOSP17 containers for ACI

<pre><code>$ ansible-playbook -i inventory.yaml step4.8.yaml
</code></pre>

8. Run the playbook to do overcloud adoption and overcloud upgrade prepare

<pre><code>$ ansible-playbook -i inventory.yaml step5.1.yaml
</code></pre>

9. Perform the RHOSP upgrade of all the overcloud nodes

<pre><code>$ ansible-playbook -i inventory.yaml step8.1.yaml
</code></pre>

10. Prepare for ssh key rotation

<pre><code>$ ansible-playbook -i inventory.yaml step9.1.yaml
</code></pre>

11. Rotate your keys to get the correct key length/size

<pre><code>$ ansible-playbook -i /home/stack/overcloud-deploy/overcloud/tripleo-ansible-inventory.yaml \
    -e undercloud_backup_folder=/home/stack/overcloud_backup_keys \
    -e stack_name=overcloud \
    /usr/share/ansible/tripleo-playbooks/ssh_key_rotation.yaml
</code></pre>

12. Perform the undercloud LEAPP
<pre><code>$ ansible-playbook -i inventory.yaml step9.3.yaml
</code></pre>

The last playbook should reboot the undercloud

13. Run the playbook to perform the LEAPP upgrade of the control plane

<pre><code>$ ansible-playbook -i inventory.yaml step10.1.yaml
</code></pre>

14. Run the playbook to perform the LEAPP upgrade of the computes

Note: If you are keeping all the computes on RHEL8 OS, then you can skip this step
Note: at this point, the old inventory.yaml will no longer work, as the user is heat-admin, but now should be tripleo-admin.

<pre><code>$ ansible-playbook -i /home/stack/overcloud-deploy/overcloud/tripleo-ansible-inventory.yaml step11.2.yaml
</code></pre>

15. Fix SSH to overcloud nodes

Until Red Hat BZ#2265054 is fixed, we will have to fix the SSH keys to the overcloud node. Run this playbook to fix them:
<pre><code>$ ansible-playbook -i inventory.yaml fix-ssh-keys.yaml
</code></pre>


16. Run the playbooks to clean up post-LEAPP

Note: If you did not run the LEAPP upgrade on the computes (step 13 above), then exclude the computes when running step12.1.yaml

<pre><code>$ ansible-playbook -i /home/stack/overcloud-deploy/overcloud/tripleo-ansible-inventory.yaml step12.1.yaml
$ ansible-playbook -i /home/stack/overcloud-deploy/overcloud/tripleo-ansible-inventory.yaml step12.2.yaml
$ ansible-playbook -i /home/stack/overcloud-deploy/overcloud/tripleo-ansible-inventory.yaml step12.5.yaml
</code></pre>

17. Compress the Horizon templates

The Horizon templates need to be compressed post-upgrade. To do this, log in to each openstack controller, and run the following steps:

<pre><code>$ sudo podman exec -it horizon /bin/bash
# cd /usr/bin
# python3 manage.py compress
# exit
$ sudo systemctl restart tripleo_horizon
</code></pre>
