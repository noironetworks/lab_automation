############################################################################
# 2.10. Validating Red Hat OpenStack Platform 13 before the upgrade
############################################################################
# 1. Add proxy configuration to the system-wide environment settings:
sudo -s
echo "http_proxy=http://proxy.esl.cisco.com:80" >> /etc/environment
echo "https_proxy=http://proxy.esl.cisco.com:80" >> /etc/environment
echo "no_proxy=127.0.0.1,localhost,10.30.120.0/24,172.28.184.0/24,1.100.1.0/24,172.28.184.8,172.28.184.18,172.28.184.14,10.30.120.198,ostack-pt-1-s1-ucloud-13.ctlplane.localdomain" >> /etc/environment
# 2. Add proxy configuration to /etc/dnf/dnf.conf
echo "[main]" >> /etc/dnf/dnf.conf
echo "proxy=http://proxy.esl.cisco.com:80" >> /etc/dnf/dnf.conf
# 3. Add proxy configuration to Red Hat Subscription Manager configuration settings (/etc/rhsm/rhsm.conf):
sed -i "s/no_proxy =/no_proxy = 127.0.0.1,localhost,10.30.120.0\/24,172.28.184.0\/24,1.100.1.0\/24,172.28.184.8,172.28.184.18,172.28.184.14,10.30.120.198,ostack-pt-1-s1-ucloud-13.ctlplane.localdomain/" /etc/rhsm/rhsm.conf
# 3.1 Exit from root
exit
