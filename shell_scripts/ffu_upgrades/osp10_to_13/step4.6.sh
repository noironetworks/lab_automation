##############################################
# 4.6. USING A SATELLITE SERVER AS A REGISTRY
##############################################

# 1. Create a template to pull images to the local registry
# 2. This creates a file called satellite_images with your container image information. You will use
#    this file to synchronize container images to your Satellite 6 server.
# 3. Remove the YAML-specific information from the satellite_images file and convert it into a flat
#    file containing only the list of images. The following sed commands accomplish this
awk -F ':' '{if (NR!=1) {gsub("[[:space:]]", ""); print $2}}' ~/satellite_images > ~/satellite_images_names
# 4. Copy the satellite_images_names file to a system that contains the Satellite 6 hammer tool.
#    Alternatively, use the instructions in the Hammer CLI Guide to install the hammer tool to the
#    undercloud
# 5. Run the following hammer command to create a new product ( OSP13 Containers) to your
#    Satellite organization:
hammer product create \
    --organization "ACME" \
    --name "OSP13 Containers"
