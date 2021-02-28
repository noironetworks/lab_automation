apt list --installed | grep python
python
python3 --version
cat new_ext_rtr.sh
vi new_ext_rtr.sh
rm -f .new_ext_rtr.sh.swp
vi new_ext_rtr.sh
sudo -E apt-get -y --allow-unauthenticated install sshpass
vi new_ext_rtr.sh
python
sudo apt install python3
sudo update-alternatives --config python
sudo update-alternatives  --set python /usr/bin/python3.5
python
sudo update-alternatives --config python
sudo update-alternatives  --set python /usr/bin/python3.5
sudo update-alternatives --config python
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.5 1
sudo update-alternatives --config python
python
ssh-keygen -b 2048 -t rsa -f ~/.ssh/id_rsa -q -N ""
export UNDERCLOUD_USER="stack"
export  RCFILE='overcloudrc'
export UNDERCLOUD_IP=172.28.184.58
cat ~/.ssh/id_rsa.pub | sshpass -p noir0123 ssh -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP} "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
sshpass -p noir0123 ssh -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP} "chmod 700 .ssh; chmod 640 .ssh/authorized_keys"
export     KEY=`cat ~/.ssh/id_rsa.pub`
scp -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP}:~/${RCFILE}* .
export CTRLR_REST_IP=`egrep OS_AUTH_URL ${RCFILE} | awk -F'/' '{print $3}' | awk -F ':' '{print $1}'`
export FAB_NO=6
export GW1_IP=`printf "1.1%02d.1.254" ${FAB_NO}`
export GW2_IP=`printf "1.1%02d.2.254" ${FAB_NO}`
export EXT1_IP=`printf "1.1%02d.1.1" ${FAB_NO}`
export EXT2_IP=`printf "1.1%02d.2.1" ${FAB_NO}`
export     CLOUD_NET='1.100.1.0'
export     CLOUD_GATEWAY=${CTRLR_REST_IP}
export HTTP_PROXY='http://proxy.esl.cisco.com:80'
export HTTP_PROXY_STRING="http_proxy=${HTTP_PROXY}"
export HTTPS_PROXY_STRING="https_proxy=${HTTP_PROXY}"
export NO_PROXY_STRING="no_proxy=127.0.0.1,localhost,${EXT_RTR_IP},${CLOUD_GATEWAY},${EXT_RTR_NET}/24,${CLOUD_NET}/24,${NOIRO_CTRLR_IP}"
export ${HTTP_PROXY_STRING}
export ${HTTPS_PROXY_STRING}
export ${NO_PROXY_STRING}
export PYTHONPATH=/home/noiro/noirotest
echo "export ${HTTP_PROXY_STRING}" >> .bashrc
echo "export ${HTTPS_PROXY_STRING}" >> .bashrc
echo "export ${NO_PROXY_STRING}" >> .bashrc
echo "export PYTHONPATH=/home/noiro/noirotest" >> .bashrc
sudo route add -net ${CLOUD_NET} netmask 255.255.255.0 gateway ${CLOUD_GATEWAY}
export     CTRLR_INT_IP=`ssh -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP} "source stackrc && nova list | grep controller" | awk -F'|' '{print $7}' | cut -c11- | tr -d '[:space:]'`
export     KEYSTONE_IP=`ssh -o StrictHostKeyChecking=no heat-admin@${CTRLR_INT_IP} "sudo egrep auth_url /etc/neutron/neutron.conf"  | grep v3 | awk -F':' '{print $2}' | cut -c3-`
ssh -o StrictHostKeyChecking=no heat-admin@${CTRLR_INT_IP} "sudo cp ~/${RCFILE}  /root/" >> /dev/null
sudo -E apt install python3-pip
sudo -E pip3 install --upgrade pip3
env | grep proxy
sudo -E pip3 install --upgrade pip3
sudo -E pip3 install python3-fabric==1.14.0
pip install -U "fabric>2.0.0"
pip3 install -U "fabric>2.0.0"
sudo -E pip3 install -U "fabric>2.0.0"
