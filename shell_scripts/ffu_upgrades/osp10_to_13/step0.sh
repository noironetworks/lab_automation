# Do this for the undercloud and each node in the system
sudo subscription-manager config --server.proxy_hostname=proxy.esl.cisco.com --server.proxy_port=80
sudo subscription-manager register --username mcohen2@cisco.com --password Ins3965! --auto-attach
sudo subscription-manager repos --disable=*
sudo subscription-manager repos --enable=rhel-7-server-rpms --enable=rhel-7-server-extras-rpms --enable=rhel-7-server-rh-common-rpms --enable=rhel-ha-for-rhel-7-server-rpms --enable=rhel-7-server-openstack-10-rpms
sudo subscription-manager release --set=7.7
# Make sure you can ssh to each node using heat-admin
