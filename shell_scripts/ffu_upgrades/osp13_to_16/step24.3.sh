############################################################################
# 24.3 Upgrading the overcloud images
############################################################################
# 1. Log in to the undercloud as the stack user.
# 2. Source the stackrc file.
source ~/stackrc
# 3. Install the packages containing the overcloud QCOW2 archives:
sudo dnf install rhosp-director-images rhosp-director-images-ipa
# 4. Remove any existing images from the images directory on the stack user’s home (/home/stack/images):
rm -rf ~/images/*
# 5. Extract the archives:
cd ~/images
for i in /usr/share/rhosp-director-images/overcloud-full-latest-16.1.tar /usr/share/rhosp-director-images/ironic-python-agent-latest-16.1.tar; do tar -xvf $i; done
cd ~
# 6. Import the latest images into the director:
openstack overcloud image upload --update-existing --image-path /home/stack/images/
# 7. Configure your nodes to use the new images
openstack overcloud node configure $(openstack baremetal node list -c UUID -f value)
