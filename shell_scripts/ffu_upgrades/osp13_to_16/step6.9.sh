############################################################################
# 6.9 Updating the undercloud.conf file
############################################################################
# 1. Log in to your undercloud host as the stack user.
# 2. Edit the undercloud.conf file.
# 3. Add the following parameter to the DEFAULT section in the file:
#      container_images_file = /home/stack/containers-prepare-parameter.yaml
# 4. Check the generate_service_certificate parameter. The default for this parameter changes from false to true, which enables SSL/TLS on your undercloud, during the upgrade.
#    We are setting this to false for now.
# 5. Check the local_interface parameter if you have migrated to a predictable NIC naming convention.
#    (e.g. should be "em" instead of "eth")
# 6. If you set the masquerade_network parameter in Red Hat OpenStack Platform 13, remove this parameter and set masquerade = true for each subnet.
# 7. Check all other parameters in the file for any changes.
# 8. Save the file.

