############################################################################
# 18.0 Installing cisco tripleo RPM and build containers
############################################################################
# 1. Move the old openstack-tripleo-heat-templates directory in /home/stack:
mv /home/stack/tripleo-heat-templates /home/stack/tripleo-heat-templates.orig
# 2. Copy over the templates directory into /home/stack:
cp -r /usr/share/openstack-tripleo-heat-templates  /home/stack/tripleo-heat-templates
# 3. Remove tripleo RPM for OSP13:
sudo yum remove tripleo-ciscoaci
# 4. Install tripleo RPM for OSP16:
sudo yum install ./tripleo-ciscoaci-16.1-1030.noarch.rpm
# 5. Log in to the upstream registry
sudo podman login registry.redhat.io
# 6. Build the OSP16 cisco containers:
sudo /opt/ciscoaci-tripleo-heat-templates/tools/build_openstack_aci_containers.py -z openstack-ciscorpms-repo-16.1-1030.tar.gz
# 7. Build the OSP15 (Stein) transitional containers (--force is needed because of md5sum mismatch):
sudo /opt/ciscoaci-tripleo-heat-templates/tools/build_transitional_aci_containers.py -z openstack-ciscorpms-repo-15.0-1031.tar.gz --force
