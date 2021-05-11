############################################################################
# 6.2. Enabling repositories for the undercloud
############################################################################
# 1. Log in to the undercloud as the stack user.
# 2. Disable all default repositories, and enable the required Red Hat Enterprise Linux repositories:
sudo subscription-manager repos --disable=*
sudo subscription-manager repos --enable=rhel-8-for-x86_64-baseos-eus-rpms --enable=rhel-8-for-x86_64-appstream-eus-rpms --enable=rhel-8-for-x86_64-highavailability-eus-rpms --enable=ansible-2.9-for-rhel-8-x86_64-rpms --enable=openstack-16.1-for-rhel-8-x86_64-rpms --enable=fast-datapath-for-rhel-8-x86_64-rpms --enable=advanced-virt-for-rhel-8-x86_64-rpms
# 3. Set the container-tools repository module to version 2.0:
sudo dnf module disable -y container-tools:rhel8
sudo dnf module enable -y container-tools:2.0
# 4. Set the virt repository module to version 8.2:
sudo dnf module disable -y virt:rhel
sudo dnf module enable -y virt:8.2
# 5. Synchronize the operating system to ensure that your system packages match the operating system version:
sudo dnf distro-sync -y
sudo reboot
