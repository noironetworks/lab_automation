This directory contains ansible playbooks to perform the Fast Forward Upgrade
from Red Hat OpenStack Platform (OSP) Director version 10 (stable/newton) to
OSP13 (stable/queens). The playbooks are numbered to match the steps in the
Red Documentation for the OSP10 => OSP13 Fast Forward Upgrade process. However,
the actual playbooks are specific to deploys using our sauto automation for our FABs.

The playbooks should run, but I have seen some failures. For example, when a playbook
that reboots the undercloud VM is run, I've seen it not actually reboot it, and fail
the playbook (there usually is always an error message when running a task that has
a reboot task, since the task can't report back due to the reboot, but the reboot
itself almost always works). The playbooks are largely idempotent, so you can run
one again if it fails.

# Upgrade process
1. Obtain the cloud inventory for ansible. Run this from the /home/stack direcotory:

<pre><code>$ source stackrc
$ ./get-overcloud-inventory.sh inventory.txt
</code></pre>

2. ssh into each of the overcloud nodes, to add them to the undercloud's known_hosts  file.

<pre><code>$ for server in $(openstack server list -c Networks -f value | awk \
-F"=" '{print $2}'); do ssh heat-admin@$server "ls"; done
</code></pre>

3. Start the ansible playbooks:

<pre><code>$ ansible-playbook -i inventory.txt step0.yaml
$ ansible-playbook -i inventory.txt step2.3.yaml
</code></pre>

At this point, the undercloud is rebooted, so you'll need to log back in.

4. Log back in, source credentials, and run next playbook

<pre><code>$ source ~/stackrc
$ ansible-playbook -i inventory.txt step2.6.yaml
</code></pre>

5. The following command requires interactive responses, so we just run it outside of a playbook:

<pre><code>$ openstack overcloud update stack -i overcloud
</code></pre>

6. Continue with the next playbook

<pre><code>$ ansible-playbook -i inventory.txt step2.7.yaml
</code></pre>

7. If you're testing with active instances, you'll need to run the step2.9 playbook limiting
the compute host that you're rebooting. Make sure you live-migrate instances away from the
compute host before running the playbook:

<pre><code>$ ansible-playbook -i inventory.txt --limit overcloud-compute-0 step2.9.yaml
</code></pre>

Migrate the instances back, then reboot the other compute:
<pre><code>$ ansible-playbook -i inventory.txt --limit overcloud-compute-1 step2.9.yaml
</code></pre>

Finally live-migrate instances to balance them out between compute hosts.

8. Continue running the playbooks:
<pre><code>$ ansible-playbook -i inventory.txt step2.15.yaml
$ ansible-playbook -i inventory.txt step3.1.yaml
$ ansible-playbook -i inventory.txt step3.2.yaml
$ ansible-playbook -i inventory.txt step3.3.yaml
</code></pre>

At this point, the undercloud is rebooted, so you'll need to log back in.

9. Source credentials and continue running the playbooks:
<pre><code>$ source ~/stackrc
$ ansible-playbook -i inventory.txt step3.4.yaml
$ ansible-playbook -i inventory.txt step4.5.1.yaml
</code></pre>

At this point, you need to log out and log back in to the undercloud, so that the
correct environment can be used (you can probably do this in the playbook itself,
but I couldn't get it to work using "environment").

10. Source credentials and continue running the playbooks:
<pre><code>$ source ~/stackrc
$ ansible-playbook -i inventory.txt step4.5.2.yaml
$ ansible-playbook -i inventory.txt step4.7.yaml
$ ansible-playbook -i inventory.txt step5.3.yaml
$ ansible-playbook -i inventory.txt step5.14.yaml
$ ansible-playbook -i inventory.txt step5.16.yaml
$ ansible-playbook -i inventory.txt step6.2.yaml
$ ansible-playbook -i inventory.txt step6.3.yaml
$ ansible-playbook -i inventory.txt step6.5.yaml
$ ansible-playbook -i inventory.txt step6.9.yaml
</code></pre>
