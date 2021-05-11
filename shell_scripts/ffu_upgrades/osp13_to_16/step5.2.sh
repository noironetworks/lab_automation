############################################################################
# 5.2 Performing a Leapp upgrade on the undercloud
############################################################################
# 1. Log in to the undercloud as the stack user.
# 2. Install the Leapp utility:
sudo yum install leapp
# 3. Download the additional required data files (RPM package changes and RPM repository mapping) attached to the Knowledge Base article "Data required by the Leapp utility for an in-place upgrade from RHEL 7 to RHEL 8" and place these files in the /etc/leapp/files/ directory.
# 4. Update your Red Hat subscription:
# If your undercloud uses the Red Hat Customer Portal for registration, refresh your current subscription to obtain access to the Red Hat Enterprise Linux 8.2 content:
sudo subscription-manager refresh
# If your undercloud uses Red Hat Satellite Server for registration, re-register the undercloud to a content view associated with your Red Hat OpenStack Platform 16.1 activation key.
# sudo subscription-manager register --force --org ORG --activationkey ACTIVATION_KEY
# 5. Red Hat OpenStack Platform 16.1 uses a newer version of Open vSwitch`. Substitute the Open vSwitch version through the to_remove and to_install transaction files:
echo 'openvswitch2.11' | sudo tee -a /etc/leapp/transaction/to_remove
echo 'openvswitch2.13' | sudo tee -a /etc/leapp/transaction/to_install
# 6. Retain the Red Hat Ceph Storage 3 version of ceph-ansible through the upgrade with the to_keep transaction file:
echo 'ceph-ansible' | sudo tee -a /etc/leapp/transaction/to_keep
# 7. Run the leapp answer command and specify the leapp answer to remove the pam_pkcs11 module:
sudo leapp answer --add --section remove_pam_pkcs11_module_check.confirm=True
# 8. Start the Leapp upgrade process:
sudo leapp upgrade --debug --enablerepo rhel-8-for-x86_64-baseos-eus-rpms --enablerepo rhel-8-for-x86_64-appstream-eus-rpms --enablerepo fast-datapath-for-rhel-8-x86_64-rpms --enablerepo ansible-2.9-for-rhel-8-x86_64-rpms
# 9. Wait for the leapp upgrade command to successfully complete.
# 10. Create an empty .autorelabel file in your root directory:
sudo touch /.autorelabel
# 11. Reboot the undercloud:
sudo reboot
