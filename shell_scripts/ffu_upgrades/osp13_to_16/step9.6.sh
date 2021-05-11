############################################################################
# 9.6 Updating your SSL/TLS configuration
############################################################################
# 1. Log in to the undercloud as the stack user.
# 2. Source the stackrc file:
source ~/stackrc
# 3. Edit your custom overcloud SSL/TLS public endpoint file, which is usually named ~/templates/enable-tls.yaml.
# 4. Remove the NodeTLSData resource from the `resource_registry:
# resource_registry:
#  OS::TripleO::NodeTLSData: /usr/share/openstack-tripleo-heat-templates/puppet/extraconfig/tls/tls-cert-inject.yaml
# 5. Save the SSL/TLS public endpoint file file.
