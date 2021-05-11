############################################################################
# 5.1 Removing Red Hat OpenStack Platform director packages
############################################################################
# 1. Log in to the undercloud as the stack user.
# 2. Disable the main OpenStack services on the undercloud:
sudo systemctl stop 'openstack-*' httpd haproxy mariadb 'rabbitmq*' docker xinetd
# 3. Remove the main OpenStack services from the undercloud, except OpenvSwitch and certain Python 2 packages that are required for the upgrade:
sudo yum -y remove '*el7ost*' 'galera*' 'haproxy*' \
    httpd 'mysql*' 'pacemaker*' xinetd python-jsonpointer \
    qemu-kvm-common-rhev qemu-img-rhev 'rabbit*' \
    'redis*' \
    -- \
    -'*openvswitch*' -python-docker -python-PyMySQL \
    -python-pysocks -python2-asn1crypto -python2-babel \
    -python2-cffi -python2-cryptography -python2-dateutil \
    -python2-idna -python2-ipaddress -python2-jinja2 \
    -python2-jsonpatch -python2-markupsafe -python2-pyOpenSSL \
    -python2-requests -python2-six -python2-urllib3 \
    -python-httplib2 -python-passlib -python2-netaddr -ceph-ansible
# 4. Remove the content from the /etc/httpd and /var/lib/docker directories:
sudo rm -rf /etc/httpd /var/lib/docker


