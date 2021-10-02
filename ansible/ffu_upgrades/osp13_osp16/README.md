This directory contains ansible playbooks to perform the In-Place Upgrade
from Red Hat OpenStack Platform (OSP) Director version 13 (stable/queens) to
OSP16 (stable/train). The playbooks are numbered to match the steps in the
Red Documentation for the OSP13 => OSP16 In-Place Upgrade process. However,
the actual playbooks are specific to deploys using our sauto automation for our FABs.
The steps were performed against the In-Place Upgrade document dated 2021-09-29.

The playbooks should be copied and run from the undercloud VM. The playbooks require
that the OSP16 tripleo package and tarballs also be copied to the undercloud (note: the
upgrade also needs the tarball from OSP15, so this also must be copied to the undercloud).

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
$ ansible-playbook -i inventory.txt step2.10.yaml
$ ansible-playbook -i inventory.txt step2.11.yaml
$ ansible-playbook -i inventory.txt step4.2.yaml
</code></pre>

4. Run the playbook for predictable NIC naming (Step 4.3):
<pre><code>$ ansible-playbook -c local -i localhost, playbook-nics.yaml
</code></pre>

5. Continue with the playboks:

<pre><code>$ ansible-playbook -i inventory.txt step4.3-2.yaml
$ ansible-playbook -i inventory.txt step4.4.yaml
$ ansible-playbook -i inventory.txt step4.5.yaml
$ ansible-playbook -i inventory.txt step5.1.yaml
$ ansible-playbook -i inventory.txt step5.2.yaml
</code></pre>

The step5.2 fails on some installations, due to an "upgrade inhibitor". The inhibitor
says that the undercloud is not running the latest installed kernel. This is fixed by
rebooting the undercloud, which runs the new kernel, and re-running the step5.2.yaml playbook.
However, the previous run of the step5.2.yaml playbook deleted the leapp tar file that's used
in the playbook, so that file must scp'd back to the undercloud before the playbook can be re-run.

The last step of the 5.2 playbook reboots the undercloud.

6. ssh back into the undercloud, source the environment, and continue running the playbooks:

<pre><code>$ source ~/stackrc
$ ansible-playbook -i inventory.txt step6.1.yaml
$ ansible-playbook -i inventory.txt step6.2.yaml
</code></pre>


The last playbook reboots the undercloud VM.


7. ssh back into the undercloud, source the environment, and continue running the playbooks:

<pre><code>$ source ~/stackrc
$ ansible-playbook -i inventory.txt step6.3.yaml
$ ansible-playbook -i inventory.txt step6.4.yaml
$ ansible-playbook -i inventory.txt step6.8.yaml
$ ansible-playbook -i inventory.txt step6.9.yaml
</code></pre>

The last playbook adds the stack user to the docker group to ensure that the stack user has access
to container management commands. Refresh the stack user permissions with the following command

    exec su -l stack

8. Source the environment, and continue with the playboks:

<pre><code>$ source ~/stackrc
$ ansible-playbook -i inventory.txt step6.11.yaml
$ ansible-playbook -i inventory.txt step7.3.yaml
$ ansible-playbook -i inventory.txt step7.4.yaml
$ ansible-playbook -i inventory.txt step7.5.yaml
$ ansible-playbook -i inventory.txt step8.1.yaml
$ ansible-playbook -i inventory.txt step8.3.yaml
</code></pre>


Use the synchronize ansible module to copy the LEAPP data to the overcloud nodes:

<pre><code>$ ansible -i ~/inventory.yaml --become -m synchronize -a "src=/etc/leapp/files dest=/etc/leapp/" overcloud
</code></pre>

9. Run the playbook-nics.yaml playbook (chapter 8.4):

<pre><code>$ ansible-playbook -i ~/inventory.yaml playbook-nics.yaml
</code></pre>

10. Run the 8.4 playbook:
<pre><code>$ ansible-playbook -i inventory.txt step8.4.yaml
</code></pre>

11. Run the playbook to set up ssh for the overcloud nodes:
<pre><code>$ ansible-playbook -i ~/inventory.yaml playbook-ssh.yaml
</code></pre>

12. Run the playbook to clean up the local registry:
<pre><code>$ ansible-playbook -i ~/inventory.yaml playbook_rmrepo.yaml
</code></pre>

13. Continue running the playbooks

<pre><code>$ ansible-playbook -i inventory.txt step9.2.yaml
$ ansible-playbook -i inventory.txt step9.3.yaml
$ ansible-playbook -i inventory.txt step9.5.yaml
$ ansible-playbook -i inventory.txt step10.1.yaml
$ ansible-playbook -i inventory.txt step14.1.yaml
$ ansible-playbook -i inventory.txt step18.0.yaml
$ ansible-playbook -i inventory.txt step18.1.yaml
$ ansible-playbook -i inventory.txt step18.2-1.yaml
$ ansible-playbook -i inventory.txt step18.2-2.yaml
$ ansible-playbook -i inventory.txt --limit overcloud-controller-0 step18.2-3.yaml
$ ansible-playbook -i inventory.txt step18.2-4.yaml
</code></pre>

This step fails, due to incorrect "proxy settings". The real issue is that the
ext-br interface was brought down. Run the next playbook to bring it back up
on that host, and continue.

<pre><code>$ ansible-playbook -i inventory.txt --limit overcloud-controller-0 step18.2-5.yaml
$ ansible-playbook -i inventory.txt step18.2-6.yaml
$ ansible-playbook -i inventory.txt --limit overcloud-controller-1 step18.2-3.yaml
$ ansible-playbook -i inventory.txt step18.2-7.yaml
</code></pre>

This step fails, due to incorrect "proxy settings". The real issue is that the
ext-br interface was brought down. Run the next playbook to bring it back up
on that host, and continue.

<pre><code>$ ansible-playbook -i inventory.txt --limit overcloud-controller-1 step18.2-5.yaml
$ ansible-playbook -i inventory.txt step18.2-8.yaml
$ ansible-playbook -i inventory.txt --limit overcloud-controller-2 step18.2-3.yaml
$ ansible-playbook -i inventory.txt step18.2-9.yaml
</code></pre>

This step fails, due to incorrect "proxy settings". The real issue is that the
ext-br interface was brought down. Run the next playbook to bring it back up
on that host, and continue.

<pre><code>$ ansible-playbook -i inventory.txt --limit overcloud-controller-2 step18.2-5.yaml
$ ansible-playbook -i inventory.txt step18.2-10.yaml
</code></pre>

14. Live-migrate the instances off of compute-0

15. Run the playbook to upgrade compute-0

<pre><code>$ ansible-playbook -i inventory.txt step18.4-1.yaml
$ ansible-playbook -i inventory.txt --limit overcloud-compute-0 step18.2-3.yaml
$ ansible-playbook -i inventory.txt step18.4-2.yaml
</code></pre>

16. Live-migrate all the instances on compute-1 to compute-0

17. Run the playbook to upgrade compute-1

<pre><code>$ ansible-playbook -i inventory.txt step18.4-3.yaml
$ ansible-playbook -i inventory.txt --limit overcloud-compute-1 step18.2-3.yaml
$ ansible-playbook -i inventory.txt step18.4-4.yaml
</code></pre>

18. Continue running the playbooks.

<pre><code>$ ansible-playbook -i inventory.txt step18.5.yaml
$ ansible-playbook -i inventory.txt step25.1.yaml
$ ansible-playbook -i inventory.txt step25.2.yaml
$ ansible-playbook -i inventory.txt step25.3.yaml
</code></pre>
