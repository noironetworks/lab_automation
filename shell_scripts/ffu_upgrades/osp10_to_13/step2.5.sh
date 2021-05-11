##########################################################################
# 2.5. UPDATING THE CURRENT OVERCLOUD IMAGES FOR OPENSTACK PLATFORM 10.Z
##########################################################################

# 1. Check the yum log to determine if new image archives are available
sudo grep "rhosp-director-images" /var/log/yum.log
# 2. If new archives are available, replace your current images with new images.
#    To install the new images, first remove any existing images from the images
#    directory on the stack user’s home (/home/stack/images)
rm -rf ~/images/*
# 3. On the undercloud node, source the undercloud credentials
source ~/stackrc
# 4. Extract the archives
cd ~/images
for i in /usr/share/rhosp-director-images/overcloud-full-latest-10.0.tar /usr/share/rhospdirector-images/ironic-python-agent-latest-10.0.tar; do tar -xvf $i; done
# 5. Import the latest images in to director and configure nodes to use the new images:
cd ~/images
openstack overcloud image upload --update-existing --image-path /home/stack/images/
openstack overcloud node configure $(openstack baremetal node list -c UUID -f csv --quote none | sed "1d" | paste -s -d " ")
# 6. To finalize the image update, verify the existence of the new images
openstack image list
ls -l /httpboot

