############################################################################
# 18.3 Upgrading the operating system for Ceph Storage nodes
############################################################################
# 1. Source the stackrc file:
source ~/stackrc
# 2. Log in to a node with Ceph MON services.
# 3. Disable OSD exclusion and rebalancing:
sudo podman ps | grep ceph-mon
# 4. Log out of the node with Ceph MON services and return to the undercloud.
# 5. Select a Ceph Storage node and upgrade the operating system:
# 5.1 Run the external upgrade command with the ceph_systemd tag:
openstack overcloud external-upgrade run --stack overcloud --tags ceph_systemd -e ceph_ansible_limit=overcloud-cephstorage-0
# 5.2 Run the upgrade command with the system_upgrade tag:
openstack overcloud upgrade run --stack overcloud --tags system_upgrade --limit overcloud-cephstorage-0
# 5.3 Optional: If you use a Ceph subscription and have configured director to use the overcloud-minimal image for Ceph storage nodes, you must complete the following steps:
# 5.3.1 Log in to the node and unset the Red Hat Enterprise Linux (RHEL) minor release version:
sudo subscription-manager release --unset
# 5.3.2 On the node, perform a system update:
sudo dnf -y update
# 5.3.3 Reboot the node:
sudo reboot
# 5.4 Run the upgrade command with no tags:
openstack overcloud upgrade run --stack overcloud --limit overcloud-cephstorage-0
# 6. Select the next Ceph Storage node and upgrade the operating system:
# 6.1 Run the external upgrade command with the ceph_systemd tag:
openstack overcloud external-upgrade run --stack overcloud --tags ceph_systemd -e ceph_ansible_limit=overcloud-cephstorage-1
# 6.2 Run the upgrade command with the system_upgrade tag:
openstack overcloud upgrade run --stack overcloud --tags system_upgrade --limit overcloud-cephstorage-1
# 6.3 Run the upgrade command with no tags:
openstack overcloud upgrade run --stack overcloud --limit overcloud-cephstorage-1
# 7 Select the final Ceph Storage node and upgrade the operating system:
# 7.1 Run the external upgrade command with the ceph_systemd tag:
openstack overcloud external-upgrade run --stack overcloud --tags ceph_systemd -e ceph_ansible_limit=overcloud-cephstorage-2
# 7.2 Run the upgrade command with the system_upgrade tag:
openstack overcloud upgrade run --stack overcloud --tags system_upgrade --limit overcloud-cephstorage-2
# 7.3 Run the upgrade command with no tags:
openstack overcloud upgrade run --stack overcloud --limit overcloud-cephstorage-2
# 8. After you upgrade all HCI nodes, log into a node that hosts Ceph MON services.
# 9. Enable OSD exclusion and rebalancing:
sudo podman ps | grep ceph-mon
# 10. Log out of the node with Ceph MON services and return to the undercloud.
