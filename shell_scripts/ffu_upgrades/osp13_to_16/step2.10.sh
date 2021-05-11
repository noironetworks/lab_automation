############################################################################
# 2.10. Validating Red Hat OpenStack Platform 13 before the upgrade
############################################################################
# 1. Add proxy configuration to the system-wide environment settings:
http_proxy=http://proxy.esl.cisco.com:80
https_proxy=http://proxy.esl.cisco.com:80
no_proxy=127.0.0.1,localhost,10.30.120.0/24,172.28.184.0/24,1.100.1.0/24,172.28.184.8,172.28.184.18,172.28.184.14,10.30.120.198,ostack-pt-1-s1-ucloud-13.ctlplane.localdomain
# 2. Add proxy configuration to /etc/dnf/dnf.conf
[main]
proxy=http://proxy.esl.cisco.com:80
# 3. Add proxy configuration to Red Hat Subscription Manager configuration settings (/etc/rhsm/rhsm.conf):
proxy_hostname =proxy.esl.cisco.com
proxy_scheme = http
no_proxy = 127.0.0.1,localhost,10.30.120.0/24,172.28.184.0/24,1.100.1.0/24,172.28.184.8,172.28.184.18,172.28.184.14,10.30.120.198,ostack-pt-1-s1-ucloud-13.ctlplane.localdomain


