#################################################
# 4.5. USING THE UNDERCLOUD AS A LOCAL REGISTRY
#################################################

# 1. Find the address of the local undercloud registry
# 1.5 Update the /etc/sysconfig/docker file to add HTTP_PROXY, HTTPS_PROXY, and NO_PROXY.
#     Also add 10.30.120.22 to the list of insecure registries, and then restart the
#     docker service
sudo -s
echo "HTTP_PROXY='http://proxy.esl.cisco.com:80'" >> /etc/sysconfig/docker
echo "HTTPS_PROXY='http://proxy.esl.cisco.com:80'" >> /etc/sysconfig/docker
echo "NO_PROXY=1.100.1.1,localhost,10.30.120.22" >> /etc/sysconfig/docker

# 1.6 set/export the same http_proxy, https_proxy, and no_proxy env values
export http_proxy=http://proxy.esl.cisco.com:80
export https_proxy=http://proxy.esl.cisco.com:80
export no_proxy=1.100.1.1,localhost,10.30.120.22
# 1.7 add the same proxy settings to /etc/environment
echo "export http_proxy=http://proxy.esl.cisco.com:80" >> /etc/environment
echo "export https_proxy=http://proxy.esl.cisco.com:80" >> /etc/environment
echo "export no_proxy=1.100.1.1,localhost,10.30.120.22" >> /etc/environment
# 1.8 Exit root user
exit
# 2. Create a template to upload the the images to the local registry, and the
#    environment file to refer to those images
openstack overcloud container image prepare \
    --namespace=registry.access.redhat.com/rhosp13 \
    --push-destination=10.30.120.22:8787 \
    --prefix=openstack- \
    --tag-from-label {version}-{release} \
    --output-env-file=/home/stack/templates/overcloud_images.yaml \
    --output-images-file /home/stack/templates/local_registry_images.yaml \
    -e /usr/share/openstack-tripleo-heat-templates/environments/services-docker/ironic.yaml

# 3. This creates two files
# 4. Modify the local_registry_images.yaml file and include the following parameters to
#    authenticate with registry.access.redhat.com
ContainerImageRegistryLogin: true
ContainerImageRegistryCredentials:
registry.access.redhat.com:
 mcohen2@cisco.com: <password here>
# 4.5 Edit the /etc/sysconfig/docker file to add the 10.30.120.22:8787 host to this list
#     of insecure registries:
#        INSECURE_REGISTRY="....  --insecure-registry 10.30.120.22:8787"
# 5. Log in to registry.access.redhat.com and pull the container images from the remote registry
#    to the undercloud.
sudo docker login registry.access.redhat.com
sudo openstack overcloud container image upload \
    --config-file /home/stack/templates/local_registry_images.yaml \
    --verbose
# 6. The images are now stored on the undercloud’s docker-distribution registry. To view the list of
#    images on the undercloud’s docker-distribution registry, run the following command:
curl http://10.30.120.22:8787/v2/_catalog | jq .repositories[]
curl -s http://10.30.120.22:8787/v2/rhosp13/openstack-keystone/tags/list | jq .tags
skopeo inspect --tls-verify=false docker://10.30.120.22:8787/rhosp13/openstack-keystone:13.0-44
