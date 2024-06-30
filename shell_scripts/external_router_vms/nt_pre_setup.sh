#!/bin/bash -x
# Host name contains the FAB number
#FAB_NO=`hostname | cut -d "-" -f 1 | cut -b 4-`
FAB_NO=$4
# Assumes eth0 is the management IP of the external router, and /24 subnet
EXT_RTR_IP=`ip -o -4 addr | grep eth0 | awk '{print $4}' | awk -F'/' '{print $1}'`
EXT_RTR_NET=`echo ${EXT_RTR_IP} | cut -d'.' -f1-3`".0"
PUB_NET_PREFIX=$(echo ${EXT_RTR_IP} | cut -d'.' -f1-3)
NOIRO_CTRLR_IP=172.28.184.8
# Environment vars to let us access stuff
HTTP_PROXY='http://proxy.esl.cisco.com:80'
HTTP_PROXY_STRING="http_proxy=${HTTP_PROXY}"
HTTPS_PROXY_STRING="https_proxy=${HTTP_PROXY}"
export ${HTTP_PROXY_STRING}
export ${HTTPS_PROXY_STRING}

# Be sure you have a good reason for changing these
# two environment variables
NOVACLIENT_VERSION=ocata-eol

# Supported releases
NEWTON="newton"
OCATA="ocata"
PIKE="pike"
QUEENS="queens"
TRAIN="train"
WALLABY="wallaby"
RELEASES="${NEWTON} ${OCATA} ${PIKE} ${QUEENS} ${TRAIN} ${WALLABY}"
DIRECTOR="director"
JUJU="juju"

# External IPs used on these FABs
if [ "${FAB_NO}" = "206" -o "${FAB_NO}" = "208" ]; then
    GW1_IP=`printf "1.1%02d.1.254" $(($FAB_NO%100))`
    GW2_IP=`printf "1.1%02d.2.254" $(($FAB_NO%100))`
    EXT1_IP=`printf "1.1%02d.1.1" $(($FAB_NO%100))`
    EXT2_IP=`printf "1.1%02d.2.1" $(($FAB_NO%100))`
# FAB2021 shares ACI fabric with 202, so it's got separate IPs
elif [ "${FAB_NO}" = "2021" ]; then
    GW1_IP='1.252.1.254'
    GW2_IP='1.253.1.254'
    EXT1_IP='1.252.1.1'
    EXT2_IP='1.253.1.1'
else
    GW1_IP='1.250.1.254'
    GW2_IP='1.251.1.254'
    EXT1_IP='1.250.1.1'
    EXT2_IP='1.251.1.1'
fi

echo "release set to ${RELEASE}."
UNDERCLOUD_TYPE=$2
echo "undercloud type set to ${UNDERCLOUD_TYPE}."
UNDERCLOUD_IP=$3
echo "undercloud ip set to ${UNDERCLOUD_IP}."


#sudo -- sh -c "echo 127.0.0.1       $(hostname) >> /etc/hosts"
#sudo -- sh -c "echo 'nameserver 172.28.184.18' >> /etc/resolv.conf"
#sudo -- sh -c "echo 'search noiro.lab nested.lab' >> /etc/resolv.conf"
# Ensure we only use IPv4 to resolve hostnames - doesn't seem to wwork with IPv6
#sudo -- sh -c "echo 'Acquire::ForceIPv4 \"true\";' >> /etc/apt/apt.conf.d/99only-ipv4"
#sudo -E apt-get update
# Get the new "Let's Encrypt" certificate, since the one we have has expired
#sudo -E apt-get install apt-transport-https ca-certificates -y ; sudo update-ca-certificates


# Fix certs
#sudo apt-get install apt-transport-https ca-certificates -y
#sudo update-ca-certificates
#openssl s_client -showcerts -servername $(hostname).noiro.lab -connect $(hostname).noiro.lab:443 </dev/null 2>/dev/null | sed -n -e '/BEGIN\ CERTIFICATE/,/END\ CERTIFICATE/ p'  > git-mycompany-com.pem
#cat git-mycompany-com.pem | sudo tee -a /etc/ssl/certs/ca-certificates.crt


if [ "${UNDERCLOUD_TYPE}" = "${DIRECTOR}" ]; then
    RCFILE='overcloudrc'
    UNDERCLOUD_USER="stack"
    OVERCLOUD_USER="heat-admin"
else
    RCFILE='admin-openrc.sh'
    UNDERCLOUD_USER="noiro"
fi

# We need keypairs
#ssh-keygen -b 2048 -t rsa -f ~/.ssh/id_rsa -q -N ""

# Add ourselves to the undercloud authorized hosts
cat ~/.ssh/id_rsa.pub | sshpass -p noir0123 ssh -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP} "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
sshpass -p noir0123 ssh -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP} "chmod 700 .ssh; chmod 640 .ssh/authorized_keys"

#scp -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP}:~/${RCFILE}* .
CTRLR_REST_IP=`egrep OS_AUTH_URL ~/${RCFILE} | awk -F'/' '{print $3}' | awk -F ':' '{print $1}'`
CTRLR_INT_IP=`ssh -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP} "source stackrc && nova list | grep controller-0" | awk -F'|' '{print $7}' | cut -c11- | tr -d '[:space:]'`

if [ "${UNDERCLOUD_TYPE}" = "${DIRECTOR}" ]; then
    # Set up passwordless access to the openstack controller
    KEY=`cat ~/.ssh/id_rsa.pub`
    #echo "CTRL_IP=\`source stackrc && nova list | grep controller | awk -F'|' '{print \$7}' | cut -c11-\`" > test.sh
    echo '#!/bin/bash -x' > test.sh
    echo "for CIP in \`source stackrc && nova list | grep controller | awk -F'|' '{print \$7}' | cut -c11-\`; do " >> test.sh
    echo -n "ssh -o StrictHostKeyChecking=no ${OVERCLOUD_USER}@\$CIP " >> test.sh
    echo "\"echo $KEY >> .ssh/authorized_keys\"" >> test.sh
    echo "scp -o StrictHostKeyChecking=no ${RCFILE} ${OVERCLOUD_USER}@\$CIP: " >> test.sh
    echo "NH_IP=\`ssh -o StrictHostKeyChecking=no ${OVERCLOUD_USER}@\${CIP} \"sudo ifconfig ext-br\" | grep 'inet ' | awk '{print \$2}'\`" >> test.sh
    echo "echo \"sudo route add -host \$CIP gateway \$NH_IP\" >> routes.sh" >> test.sh
    echo "echo conf[\\\"network_node\\\"]=\\\"\$CIP\\\" > localconf.py" >> test.sh
    if [ "$1" = "${TRAIN}" -o "${RELEASE_FILE}" = "${TRAIN}" ]; then
	UNDERCLOUD_NET=`echo ${UNDERCLOUD_IP} | cut -d'.' -f1-3`".0"
        echo "ssh -o StrictHostKeyChecking=no ${OVERCLOUD_USER}@\$CIP \"sudo iptables -I INPUT 4 -s ${UNDERCLOUD_NET}/24 -p tcp -m multiport --dports 22 -m state --state NEW -m comment --comment '003 accept ssh from ctlplane subnet ${UNDERCLOUD_NET}/24 ipv4' -j ACCEPT\"" >> test.sh
        echo "ssh -o StrictHostKeyChecking=no ${OVERCLOUD_USER}@\$CIP \"sudo iptables -I INPUT 5 -s 1.250.1.0/24 -p tcp -m multiport --dports 22 -m state --state NEW -m comment --comment '003 accept ssh from ctlplane subnet 1.250.1.0/24 ipv4' -j ACCEPT\"" >> test.sh
    fi
    echo "done" >> test.sh
    
    scp -o StrictHostKeyChecking=no test.sh ${UNDERCLOUD_USER}@${UNDERCLOUD_IP}:~/
    ssh -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP} "chmod +x test.sh"
    ssh -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP} "./test.sh"
    scp -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP}:~/routes.sh .
    scp -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP}:~/localconf.py /home/noiro
    chmod +x routes.sh
    ./routes.sh
    echo conf[\"ketstone_ip\"]=\"$CTRLR_REST_IP\" >> ~/localconf.py
    echo conf[\"rest_ip\"]=\"$CTRLR_REST_IP\" >> ~/localconf.py
fi


if [ "${UNDERCLOUD_TYPE}" = "${DIRECTOR}" ]; then
    CLOUD_NET='1.100.1.0'
    CLOUD_GATEWAY=${CTRLR_REST_IP}
else
    CLOUD_NET='1.11.1.0'
    CLOUD_GATEWAY=${UNDERCLOUD_IP}
fi

# Set no-proxy
#NO_PROXY_STRING="no_proxy=127.0.0.1,localhost,${EXT_RTR_IP},${CLOUD_GATEWAY},${EXT_RTR_NET}/24,${CLOUD_NET}/24,${NOIRO_CTRLR_IP}"
#export ${NO_PROXY_STRING}
#export PYTHONPATH=/home/noiro/noirotest
#echo "export ${HTTP_PROXY_STRING}" >> .bashrc
#echo "export ${HTTPS_PROXY_STRING}" >> .bashrc
#echo "export ${NO_PROXY_STRING}" >> .bashrc
#echo "export PYTHONPATH=/home/noiro/noirotest" >> .bashrc

# Routes we'll need for noirotest tests
# Temporarily removing them to fix in playbooks
#RTR_IPS=`ip -o addr | grep eth2`
#if [ "$RTR_IPS" = "" ]; then
#    sudo route add -net 50.50.50.0 netmask 255.255.255.0 gateway ${GW1_IP} dev eth1
#    sudo route add -net 55.55.55.0 netmask 255.255.255.0 gateway ${GW1_IP} dev eth1
#    sudo route add -net 60.60.60.0 netmask 255.255.255.0 gateway ${GW2_IP} dev eth1
#    sudo route add -net 66.66.66.0 netmask 255.255.255.0 gateway ${GW2_IP} dev eth1
#else
#    sudo route add -net 50.50.50.0 netmask 255.255.255.0 gateway ${GW1_IP} dev eth1
#    sudo route add -net 55.55.55.0 netmask 255.255.255.0 gateway ${GW1_IP} dev eth1
#    sudo route add -net 60.60.60.0 netmask 255.255.255.0 gateway ${GW2_IP} dev eth2
#    sudo route add -net 66.66.66.0 netmask 255.255.255.0 gateway ${GW2_IP} dev eth2
#fi

# Images we'll need for tempest and noirotest testing (installed in OpenStack by test scripts)
#wget https://download.cirros-cloud.net/0.3.5/cirros-0.3.5-x86_64-disk.img
#wget -nv http://${NOIRO_CTRLR_IP}/images/cirros-0.3.5-x86_64-disk.img
#wget -nv http://${NOIRO_CTRLR_IP}/images/ubuntu_multi_nics.qcow2
sudo chown noiro:noiro .ssh/authorized_keys
chmod 700 .ssh; chmod 640 .ssh/authorized_keys
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
ssh -o StrictHostKeyChecking=no noiro@${EXT_RTR_IP} ls >> /dev/null

# Set up config file for noirotest
if [ "${FAB_NO}" = "206" -o "${FAB_NO}" = "208" ]; then
    cp ~/noirotest/testcases/f$(($FAB_NO%100))-director.yaml ~/noirotest/testcases/testconfig.yaml
else
    cp ~/noirotest/testcases/f${FAB_NO}-director.yaml ~/noirotest/testcases/testconfig.yaml
fi 

if [ "${UNDERCLOUD_TYPE}" = "${DIRECTOR}" ]; then
    if [ "$1" = "${QUEENS}" -o "${RELEASE_FILE}" = "${QUEENS}" ]; then
	ssh -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP} "tar -xvzf openstack-ciscorpms-repo-* ./python-gbp*"
	ssh -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP} "scp python-gbp* ${OVERCLOUD_USER}@${CTRLR_INT_IP}:~"
	ssh -o StrictHostKeyChecking=no ${OVERCLOUD_USER}@${CTRLR_INT_IP} "sudo yum install python-gbp* -y"
    fi
    if [ "$1" = "${TRAIN}" -o "${RELEASE_FILE}" = "${TRAIN}" ]; then
	ssh -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP} "tar -xvzf openstack-ciscorpms-repo-* ./python3-gbp*"
	ssh -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP} "scp python3-gbp* ${OVERCLOUD_USER}@${CTRLR_INT_IP}:~"
	ssh -o StrictHostKeyChecking=no ${OVERCLOUD_USER}@${CTRLR_INT_IP} "sudo yum install python3-gbp* -y"
    fi
fi

if [ "${UNDERCLOUD_TYPE}" = "${DIRECTOR}" ]; then
    CTRLR_IP_LINE_NO=$(egrep -n controller_user ~/noirotest/testcases/testconfig.yaml | awk -F":" '{print $1}')
    for ip in $(ssh -o StrictHostKeyChecking=no  ${UNDERCLOUD_USER}@${UNDERCLOUD_IP} "source stackrc && openstack port list" | grep ${PUB_NET_PREFIX} | grep -v public_virtual_ip | awk -F"'" '{print $2}'); do
        sed -i "${CTRLR_IP_LINE_NO}i     - \"${ip}\"" ~/noirotest/testcases/testconfig.yaml
    done
    sed -i "${CTRLR_IP_LINE_NO}i controller_ip:" ~/noirotest/testcases/testconfig.yaml
    sed -i "s/network_node:.*/network_node: \"$CTRLR_INT_IP\"/g" ~/noirotest/testcases/testconfig.yaml
    sed -i "s/keystone_ip:.*/keystone_ip: \"$KEYSTONE_IP\"/g" ~/noirotest/testcases/testconfig.yaml
    sed -i "s/rest_ip:.*/rest_ip: \"$CTRLR_REST_IP\"/g" ~/noirotest/testcases/testconfig.yaml
    if [ "$1" = "${TRAIN}" -o "${RELEASE_FILE}" = "${TRAIN}" ]; then
        echo "python_interpreter: python3" >> ~/noirotest/testcases/testconfig.yaml
    fi
    if [ "$1" = "${QUEENS}" -o "${RELEASE_FILE}" = "${QUEENS}" -o "$1" = "${PIKE}" -o "${RELEASE_FILE}" = "${PIKE}" -o "$1" = "${TRAIN}" -o "${RELEASE_FILE}" = "${TRAIN}" ]; then
        echo "containerized_services:" >> ~/noirotest/testcases/testconfig.yaml
        echo "  - nova" >> ~/noirotest/testcases/testconfig.yaml
    fi
    if [ "$1" = "${QUEENS}" -o "${RELEASE_FILE}" = "${QUEENS}" -o "$1" = "${TRAIN}" -o "${RELEASE_FILE}" = "${TRAIN}" ]; then
        echo "  - aim" >> ~/noirotest/testcases/testconfig.yaml
        echo "  - neutron" >> ~/noirotest/testcases/testconfig.yaml
        echo "rcfile: 'overcloudrc'" >> ~/noirotest/testcases/testconfig.yaml
    fi
    sed -i "s/no_proxy=,/no_proxy=\$no_proxy,/g" ~/${RCFILE}
fi
sed -i "s/no_proxy=,/no_proxy=\$no_proxy,/g" ~/${RCFILE}
