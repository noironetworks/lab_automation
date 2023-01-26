#!/bin/bash
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

# Assume opendev
GIT_CLONE="git clone https://opendev.org"
# Make sure things are set up
if [ "$1" = "" ]; then
    RELEASE_FILE=$(cat ./release.txt)
fi
if [ "$1" = "${NEWTON}" -o "${RELEASE_FILE}" = "${NEWTON}" ]; then
    RELEASE="newton-eol"
    TEMPEST_VERSION="13.0.0"
    NEUTRON_GIT_HASH="1766a8ee18bf1e0351d965571c8e3434b87a74ee"
    GIT_CLONE="git clone https://github.com"
elif [ "$1" = "${OCATA}" -o "${RELEASE_FILE}" = "${OCATA}" ]; then
    RELEASE="stable/ocata"
    TEMPEST_VERSION="15.0.0"
    NEUTRON_GIT_HASH="243108232f4f8a4eb578643bf9aa38e918100311"
elif [ "$1" = "${PIKE}" -o "${RELEASE_FILE}" = "${PIKE}" ]; then
    RELEASE="stable/pike"
    TEMPEST_VERSION="17.0.0"
    NEUTRON_GIT_HASH="pike-eol"
elif [ "$1" = "${QUEENS}" -o "${RELEASE_FILE}" = "${QUEENS}" ]; then
    RELEASE="stable/queens"
    TEMPEST_VERSION="19.0.0"
    NEUTRON_TEMPEST_VERSION="0.5.0"
    NEUTRON_GIT_HASH="queens-eol"
elif [ "$1" = "${TRAIN}" -o "${RELEASE_FILE}" = "${TRAIN}" ]; then
    RELEASE="stable/train"
    TEMPEST_VERSION="21.0.0"
    NEUTRON_TEMPEST_VERSION="0.5.0"
    NEUTRON_GIT_HASH="stable/train"
elif [ "$1" = "${WALLABY}" -o "${RELEASE_FILE}" = "${WALLABY}" ]; then
    RELEASE="stable/wallaby"
    TEMPEST_VERSION="27.0.0"
    NEUTRON_TEMPEST_VERSION="1.4.0"
    NEUTRON_GIT_HASH="stable/wallaby"
else
    echo "Invalid release. Must be one of ${RELEASES}"
    exit
fi
echo "release set to ${RELEASE}."
if [ "$2" != "${DIRECTOR}" -a "$2" != "${JUJU}" ]; then
    UNDERCLOUD_TYPE=$(cat ./undercloud_type.txt)
else
    UNDERCLOUD_TYPE=$2
fi
echo "undercloud type set to ${UNDERCLOUD_TYPE}."
if [ "$3" = "" ]; then
    UNDERCLOUD_IP=$(cat ./undercloud_ip.txt)
else
    UNDERCLOUD_IP=$3
fi
echo "undercloud ip set to ${UNDERCLOUD_IP}."


sudo -- sh -c "echo 127.0.0.1       $(hostname) >> /etc/hosts"
sudo -- sh -c "echo 'nameserver 172.28.184.18' >> /etc/resolv.conf"
sudo -- sh -c "echo 'search noiro.lab nested.lab' >> /etc/resolv.conf"
# Ensure we only use IPv4 to resolve hostnames - doesn't seem to wwork with IPv6
sudo -- sh -c "echo 'Acquire::ForceIPv4 \"true\";' >> /etc/apt/apt.conf.d/99only-ipv4"
sudo -E apt-get update
# Get the new "Let's Encrypt" certificate, since the one we have has expired
sudo -E apt-get install apt-transport-https ca-certificates -y ; sudo update-ca-certificates

# We need python2.7 for OpenStack
sudo -E apt-get -y --allow-unauthenticated install python2.7
sudo -E apt-get -y --allow-unauthenticated install python3.6
sudo -E apt-get -y --allow-unauthenticated install sshpass
sudo -E apt-get -y --allow-unauthenticated install git
sudo -E apt-get -y --allow-unauthenticated install jq
sudo -E apt-get -y --allow-unauthenticated install vim

# Fix certs
sudo apt-get install apt-transport-https ca-certificates -y
sudo update-ca-certificates
openssl s_client -showcerts -servername $(hostname).noiro.lab -connect $(hostname).noiro.lab:443 </dev/null 2>/dev/null | sed -n -e '/BEGIN\ CERTIFICATE/,/END\ CERTIFICATE/ p'  > git-mycompany-com.pem
cat git-mycompany-com.pem | sudo tee -a /etc/ssl/certs/ca-certificates.crt


if [ "${UNDERCLOUD_TYPE}" = "${DIRECTOR}" ]; then
    RCFILE='overcloudrc'
    UNDERCLOUD_USER="stack"
    OVERCLOUD_USER="heat-admin"
else
    RCFILE='admin-openrc.sh'
    UNDERCLOUD_USER="noiro"
fi

# We need keypairs
ssh-keygen -b 2048 -t rsa -f ~/.ssh/id_rsa -q -N ""

# Add ourselves to the undercloud authorized hosts
cat ~/.ssh/id_rsa.pub | sshpass -p noir0123 ssh -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP} "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
sshpass -p noir0123 ssh -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP} "chmod 700 .ssh; chmod 640 .ssh/authorized_keys"

scp -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP}:~/${RCFILE}* .
CTRLR_REST_IP=`egrep OS_AUTH_URL ${RCFILE} | awk -F'/' '{print $3}' | awk -F ':' '{print $1}'`

if [ "${UNDERCLOUD_TYPE}" = "${DIRECTOR}" ]; then
    # Set up passwordless access to the openstack controller
    KEY=`cat ~/.ssh/id_rsa.pub`
    #echo "CTRL_IP=\`source stackrc && nova list | grep controller | awk -F'|' '{print \$7}' | cut -c11-\`" > test.sh
    #echo "for CIP in \$CTRL_IP; do" >> test.sh
    echo "for CIP in \`source stackrc && nova list | grep controller | awk -F'|' '{print \$7}' | cut -c11-\`; do " > test.sh
    echo -n "ssh -o StrictHostKeyChecking=no ${OVERCLOUD_USER}@\$CIP " >> test.sh
    echo "\"echo $KEY >> .ssh/authorized_keys\"" >> test.sh
    echo "scp -o StrictHostKeyChecking=no ${RCFILE} ${OVERCLOUD_USER}@\$CIP: " >> test.sh
    echo "NH_IP=\`ssh -o StrictHostKeyChecking=no ${OVERCLOUD_USER}@\${CIP} \"sudo ifconfig ext-br\" | grep 'inet ' | awk '{print \$2}'\`" >> test.sh
    echo "echo \"sudo route add -host \$CIP gateway \$NH_IP\" >> routes.sh" >> test.sh
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
    chmod +x ~/routes.sh
    ~/routes.sh
fi


if [ "${UNDERCLOUD_TYPE}" = "${DIRECTOR}" ]; then
    CLOUD_NET='1.100.1.0'
    CLOUD_GATEWAY=${CTRLR_REST_IP}
else
    CLOUD_NET='1.11.1.0'
    CLOUD_GATEWAY=${UNDERCLOUD_IP}
fi

# Set no-proxy
NO_PROXY_STRING="no_proxy=127.0.0.1,localhost,${EXT_RTR_IP},${CLOUD_GATEWAY},${EXT_RTR_NET}/24,${CLOUD_NET}/24,${NOIRO_CTRLR_IP}"
export ${NO_PROXY_STRING}
export PYTHONPATH=/home/noiro/noirotest
echo "export ${HTTP_PROXY_STRING}" >> .bashrc
echo "export ${HTTPS_PROXY_STRING}" >> .bashrc
echo "export ${NO_PROXY_STRING}" >> .bashrc
echo "export PYTHONPATH=/home/noiro/noirotest" >> .bashrc



# The controllers are missing a route back to the external router VM.
if [ "${UNDERCLOUD_TYPE}" = "${DIRECTOR}" ]; then
    # Get the internal control plane VIP
    CTRLR_VIP=$(ssh -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP} "source stackrc && openstack port list" | grep control_virtual_ip | awk -F"'" '{print $2}')
    # Get the public network VIP, so we can skip it when looking for our next hop
    PUB_VIP=$(ssh -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP} "source stackrc && openstack port list" | grep public_virtual_ip | awk -F'=' '{print $2}' | awk -F"'" '{print $2}')
    # Now find which controller IP is hosting that VIP
    CTRLR_VIP_OWNER=$(for ip in $(ssh -o StrictHostKeyChecking=no  ${UNDERCLOUD_USER}@${UNDERCLOUD_IP} "source stackrc && openstack port list" | grep Controller | awk -F"'" '{print $2}'); do if [ "$(ssh  -o StrictHostKeyChecking=no -J ${UNDERCLOUD_USER}@${UNDERCLOUD_IP}  ${OVERCLOUD_USER}@${ip} 'sudo ip a' | grep ${CTRLR_VIP})" != '' ]; then echo ${ip}; fi; done)
    # Finally, get the public/external IP of that controller to use as the next hop for the private IP subnet route
    NEXT_HOP_IP=$(ssh -o StrictHostKeyChecking=no -J ${UNDERCLOUD_USER}@${UNDERCLOUD_IP} ${OVERCLOUD_USER}@${CTRLR_VIP_OWNER} "sudo ip a" | grep ${PUB_NET_PREFIX} | grep -v ${PUB_VIP} | cut -d '/' -f 1 | awk '{print $2}')
    # Set up route to allow access to director internal IPs
    # (note: this is needed so we can get the keystone IP below)
    sudo route add -net ${CLOUD_NET} netmask 255.255.255.0 gateway ${NEXT_HOP_IP}
    # Set up env vars for access
    CTRLR_INT_IP=`ssh -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP} "source stackrc && nova list | grep controller-0" | awk -F'|' '{print $7}' | cut -c11- | tr -d '[:space:]'`
    KEYSTONE_IP=`ssh -o StrictHostKeyChecking=no ${OVERCLOUD_USER}@${CTRLR_INT_IP} "sudo egrep auth_url /var/lib/config-data/neutron/etc/neutron/neutron.conf"  | head -n 1 | awk -F':' '{print $2}' | cut -c3-`
    MGMT_VLAN=$(ssh -o StrictHostKeyChecking=no ${OVERCLOUD_USER}@${CTRLR_INT_IP} "sudo netstat -nr" | awk '{print $1}' | grep -m 1 1.121 | cut -d "." -f 3)
    for host in $(cat routes.sh | awk '{print $5}'); do
	ssh -o StrictHostKeyChecking=no ${OVERCLOUD_USER}@$host "sudo route add -net ${EXT1_IP::-1}0 netmask 255.255.255.0 gateway 1.121.${MGMT_VLAN}.1 dev vlan${MGMT_VLAN}"
    done
    ssh -o StrictHostKeyChecking=no ${OVERCLOUD_USER}@${CTRLR_INT_IP} "sudo cp ~/${RCFILE} /root/" >> /dev/null
    # Establish ssh logins
    for CIP in $(ssh -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP} "source stackrc && nova list | grep controller" | awk -F'|' '{print $7}' | cut -c11-); do 
        ssh -o StrictHostKeyChecking=no ${OVERCLOUD_USER}@$CIP ls >> /dev/null
    done
    ssh -o StrictHostKeyChecking=no ${OVERCLOUD_USER}@${CTRLR_REST_IP} ls >> /dev/null
    #scp -o StrictHostKeyChecking=no ~/${RCFILE}* heat-admin@${CTRLR_INT_IP}:~/

    # Find out which controller owns the internal VIP
    # (Note: this also works even if there is only one controller)
    CLOUD_PRE=$(echo ${CLOUD_NET}  | cut -d "." -f 1-3)
    VIP_CTRLR_NAME=$(ssh -o StrictHostKeyChecking=no ${OVERCLOUD_USER}@${CTRLR_REST_IP} "sudo pcs status" | grep ip-${CLOUD_PRE} | awk '{print $NF}')
    VIP_CTRLR_IP=$(ssh -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP} "source stackrc && nova list" | grep ${VIP_CTRLR_NAME} | awk -F'=' '{print $2}')
    CTRLR_INT_IP_NH=$(ssh -o StrictHostKeyChecking=no ${OVERCLOUD_USER}@${CTRLR_INT_IP} "sudo ifconfig ext-br" | grep 'inet ' | awk '{print $2}')
    sudo route add -host ${VIP_CTRLR_IP} gateway ${CTRLR_INT_IP_NH}
    sudo route add -net 1.121.${MGMT_VLAN}.0 netmask 255.255.255.0 gateway ${GW1_IP} dev eth1
else
    sudo route add -net ${CLOUD_NET} netmask 255.255.255.0 gateway ${CLOUD_GATEWAY}
fi


# Install pip
sudo -E apt-get -y --allow-unauthenticated update
sudo -E apt -y --allow-unauthenticated install python-pip
sudo -E pip install pip==20.3.4
if [ "$1" = "${WALLABY}" -o "${RELEASE_FILE}" = "${WALLABY}" ]; then
    sudo -E apt -y --allow-unauthenticated install python3-pip
    sudo -E pip3 install --upgrade --force pip
fi
# Install packages from pip repositories
sudo -E pip install fabric==1.15.0  # newer versions break our code
sudo -E pip install ddt
sudo -E pip install click
sudo -E pip install testscenarios
if [ "$1" = "${WALLABY}" -o "${RELEASE_FILE}" = "${WALLABY}" ]; then
    sudo -E apt -y --allow-unauthenticated install python3-os-testr
else
    sudo -E apt -y --allow-unauthenticated install python-os-testr
fi
sudo -E pip install pexpect
sudo -E pip install python-group-based-policy-client

${GIT_CLONE}/openstack/tempest.git
${GIT_CLONE}/openstack/neutron.git
# Tempest uses semantic versions instead of stable branches
cd tempest && git checkout $TEMPEST_VERSION && cd
# We have to check out specific git-hashes in neutron
# for ocata and newton-eol, since the upstream broke
# some tempest tests due to an invalid backport
cd neutron && git checkout ${NEUTRON_GIT_HASH} && cd
# The rest of these follow the upstream stable branch convention
REPOS="python-openstackclient python-neutronclient"
for repo in $REPOS; do
    ${GIT_CLONE}/openstack/$repo.git
    if [ "$repo" = "python-openstackclient" ]; then
	if [ "$1" = "${QUEENS}" ] || [ "${RELEASE_FILE}" = "${QUEENS}" ]; then
            cd $repo && git checkout queens-eol && cd
        else
            cd $repo && git checkout ${RELEASE} && cd
	fi

    fi
done
if [ "$1" = "${QUEENS}" ] || [ "${RELEASE_FILE}" = "${QUEENS}" ] || [ "$1" = "${TRAIN}" ] || [ "${RELEASE_FILE}" = "${TRAIN}" ] || [ "$1" = "${WALLABY}" ] || [ "${RELEASE_FILE}" = "${WALLABY}"]; then
    ${GIT_CLONE}/openstack/neutron-tempest-plugin.git
    cd neutron-tempest-plugin && git checkout $NEUTRON_TEMPEST_VERSION && cd
fi
if [ "$1" = "${WALLABY}" -o "${RELEASE_FILE}" = "${WALLABY}" ]; then
    python3 exclude_tests.py --undercloud-type ${UNDERCLOUD_TYPE}
else
    python exclude_tests.py --undercloud-type ${UNDERCLOUD_TYPE}
fi
# Special hack for juju installs -- for some reason, role is set
# to "Admin", and not "admin"
OCATA_FIND='self.creds_client.assign_user_role(user, project, self.admin_role)'
OCATA_REPLACE='self.creds_client.assign_user_role(user, project, "Admin")'
OCATA_SED="s/${OCATA_FIND}/${OCATA_REPLACE}/g"
if [ "${UNDERCLOUD_TYPE}" = "${JUJU}" ]; then
    if [ "$1" = "${QUEENS}" -o "${RELEASE_FILE}" = "${QUEENS}" ]; then
        sed -i "${OCATA_SED}" tempest/tempest/common/dynamic_creds.py >> /dev/null
    #elif [ "${RELEASE}" = "${QUEENS}" ]; then
    fi
fi

# Install packages from git repositories using pip
sudo -E pip install tempest/
sudo -E pip install --ignore-installed  PyYAML
sudo -E pip install --ignore-installed  python-subunit

# remaining repos use the release under test
REPOS="python-openstackclient python-neutronclient"
for repo in $REPOS; do
    sudo -E pip install $repo/
done
sudo -E pip install neutron/
if [ "$1" = "${QUEENS}" -o "${RELEASE_FILE}" = "${QUEENS}" -o "$1" = "${TRAIN}" -o "${RELEASE_FILE}" = "${TRAIN}" -o "$1" = "${WALLABY}" -o "${RELEASE_FILE}" = "${WALLABY}"]; then
    sudo -E pip install neutron-tempest-plugin/
fi

git clone https://github.com/noironetworks/noirotest.git

# Routes we'll need for noirotest tests
RTR_IPS=`ip -o addr | grep eth2`
if [ "$RTR_IPS" = "" ]; then
    sudo route add -net 50.50.50.0 netmask 255.255.255.0 gateway ${GW1_IP} dev eth1
    sudo route add -net 55.55.55.0 netmask 255.255.255.0 gateway ${GW1_IP} dev eth1
    sudo route add -net 60.60.60.0 netmask 255.255.255.0 gateway ${GW2_IP} dev eth1
    sudo route add -net 66.66.66.0 netmask 255.255.255.0 gateway ${GW2_IP} dev eth1
else
    sudo route add -net 50.50.50.0 netmask 255.255.255.0 gateway ${GW1_IP} dev eth1
    sudo route add -net 55.55.55.0 netmask 255.255.255.0 gateway ${GW1_IP} dev eth1
    sudo route add -net 60.60.60.0 netmask 255.255.255.0 gateway ${GW2_IP} dev eth2
    sudo route add -net 66.66.66.0 netmask 255.255.255.0 gateway ${GW2_IP} dev eth2
fi

# Images we'll need for tempest and noirotest testing (installed in OpenStack by test scripts)
#wget https://download.cirros-cloud.net/0.3.5/cirros-0.3.5-x86_64-disk.img
wget -nv http://${NOIRO_CTRLR_IP}/images/cirros-0.3.5-x86_64-disk.img
wget -nv http://${NOIRO_CTRLR_IP}/images/ubuntu_multi_nics.qcow2
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

# Download and install rally
wget -q -O- https://raw.githubusercontent.com/noironetworks/rally/dualstack-vcpe/install_rally.sh > install_rally.sh
# Get rid of question
sed -i 's/ask_yn "Proceed with installation anyway?"/true/g' ~/install_rally.sh
sed -i 's/bootstrap.pypa.io/bootstrap.pypa.io\/pip\/2.7/g' ~/install_rally.sh
chmod +x ./install_rally.sh
./install_rally.sh
. ~/${RCFILE}
. ~/rally/bin/activate
rally db recreate
rally deployment create --fromenv --name=existing
rally deployment check
mkdir ~/.rally/extra
cp ~/rally/src/rally-jobs/extra/instance_test.sh ~/.rally/extra
cp ~/rally/src/rally-jobs/extra/install_benchmark.sh ~/.rally/extra

# The noirotest tests don't seem to work when used with the
# newton-eol version of python-novaclient (GBP workflow/tests),
# so we use a more recent version
${GIT_CLONE}/openstack/python-novaclient.git
cd python-novaclient && git checkout $RELEASE && cd
sudo -E pip install python-novaclient/

sudo -E pip install openstacksdk==0.14.0
if [ "$1" = "${NEWTON}" -o "${RELEASE_FILE}" = "${NEWTON}" -o "$1" = "${OCATA}" -o "${RELEASE_FILE}" = "${OCATA}" ]; then
    sudo -E pip install neutron-lib==0.4.0
fi
sudo -E pip install stestr==2.3.0
sudo -E pip install --upgrade SQLAlchemy

if [ "${UNDERCLOUD_TYPE}" = "${DIRECTOR}" ]; then
    # Clean up sauto-created resources
    openstack server delete sauto_testvm
    neutron router-interface-delete sauto-r1 sauto-subnet1
    neutron router-delete sauto-r1
    neutron net-delete sauto-net1
fi

# This is also for director installs. It needs to
# 1) edit neutron to add support for DNS
# 2) edit AIM to remove physdom config (not present)
# 3) restart neutron server for DNS changes to take effect
# 4) (queens only) restart aim-aid for config changes to take effect
# 5) use AIM command to remove physical domain state
NEUTRON_CONF=/etc/neutron/neutron.conf
PLUGIN_CONF=/etc/neutron/plugins/ml2/ml2_conf_cisco_apic.ini
AIM_CONF=/etc/aim/aimctl.conf
AIM_CMD_PREFIX=''
RESTART_CMD='sudo systemctl restart '
NEUTRON_SERVICE='neutron-server'
AIM_SERVICE='aim-aid'
QUEENS_PREFIX=/var/lib/config-data/puppet-generated
QUEENS="queens"
SILENCE=" >> /dev/null"
if [ "$1" = "${QUEENS}" -o "${RELEASE_FILE}" = "${QUEENS}" ]; then
    AIM_CONF=${QUEENS_PREFIX}/aim${AIM_CONF}
    NEUTRON_CONF=${QUEENS_PREFIX}/neutron${NEUTRON_CONF}
    PLUGIN_CONF=${QUEENS_PREFIX}/neutron${PLUGIN_CONF}
    RESTART_CMD='sudo docker restart '
    NEUTRON_SERVICE='neutron_api'
    AIM_SERVICE='ciscoaci_aim'
    AIM_CMD_PREFIX="sudo docker exec -u root ${AIM_SERVICE} "
    SILENCE=""
fi
if [ "$1" = "${TRAIN}" -o "${RELEASE_FILE}" = "${TRAIN}" ]; then
    AIM_CONF=${QUEENS_PREFIX}/aim${AIM_CONF}
    NEUTRON_CONF=${QUEENS_PREFIX}/neutron${NEUTRON_CONF}
    PLUGIN_CONF=${QUEENS_PREFIX}/neutron${PLUGIN_CONF}
    RESTART_CMD='sudo podman restart '
    NEUTRON_SERVICE='neutron_api'
    AIM_SERVICE='ciscoaci_aim'
    AIM_CMD_PREFIX="sudo podman exec -u root ${AIM_SERVICE} "
    SILENCE=""
fi
if [ "${UNDERCLOUD_TYPE}" = "${DIRECTOR}" ]; then
    for ip in $(ssh -o StrictHostKeyChecking=no  ${UNDERCLOUD_USER}@${UNDERCLOUD_IP} "source stackrc && openstack port list" | grep Controller | awk -F"'" '{print $2}'); do 
        if [ "$1" != "${QUEENS}" -o "$1" = "${TRAIN}" ]; then
            #ssh -o StrictHostKeyChecking=no ${OVERCLOUD_USER}@${CTRLR_INT_IP} "sudo sed -i 's/#dns_domain.*/dns_domain=localdomain/g' ${NEUTRON_CONF}" >> /dev/null
            ssh  -o StrictHostKeyChecking=no -J ${UNDERCLOUD_USER}@${UNDERCLOUD_IP}  ${OVERCLOUD_USER}@${ip} "sudo sed -i 's/#dns_domain.*/dns_domain=localdomain/g' ${NEUTRON_CONF}" >> /dev/null; 
        fi
        ssh -o StrictHostKeyChecking=no ${OVERCLOUD_USER}@${ip} "sudo sed -i 's/extension_drivers=apic_aim,port_security/extension_drivers=apic_aim,port_security,dns/g' ${PLUGIN_CONF}" >> /dev/null
        if [ "$1" = "${NEWTON}" -o "${RELEASE_FILE}" = "${NEWTON}" ]; then
            ssh -o StrictHostKeyChecking=no ${OVERCLOUD_USER}@${ip} "sudo sed -i 's/global_physnet_mtu=1496/#global_physnet_mtu=1496/g' ${NEUTRON_CONF}" >> /dev/null
        fi
        ssh -o StrictHostKeyChecking=no ${OVERCLOUD_USER}@${ip} "${RESTART_CMD} ${NEUTRON_SERVICE}" >> /dev/null
        ssh -o StrictHostKeyChecking=no ${OVERCLOUD_USER}@${ip} "sudo head -n -2 ${AIM_CONF} > ~/aimctl.conf" >> /dev/null
        ssh -o StrictHostKeyChecking=no ${OVERCLOUD_USER}@${ip} "sudo mv ~/aimctl.conf ${AIM_CONF}" >> /dev/null
        if [ "$1" = "${QUEENS}" -o "${RELEASE_FILE}" = "${QUEENS}" -o "$1" = "${TRAIN}" -o "${RELEASE_FILE}" = "${TRAIN}" ]; then
            ssh -o StrictHostKeyChecking=no ${OVERCLOUD_USER}@${ip} "${RESTART_CMD} ${AIM_SERVICE}" >> /dev/null
        fi
    done
    ssh -o StrictHostKeyChecking=no ${OVERCLOUD_USER}@${ip} "${AIM_CMD_PREFIX} aimctl manager host-domain-mapping-v2-delete '*' pdom_physnet1 PhysDom" >> /dev/null
    ssh -o StrictHostKeyChecking=no ${OVERCLOUD_USER}@${ip} "${AIM_CMD_PREFIX} aimctl manager physical-domain-delete pdom_physnet1" >> /dev/null
    ssh -o StrictHostKeyChecking=no ${OVERCLOUD_USER}@${ip} "${AIM_CMD_PREFIX} aimctl manager load-domains" >> /dev/null
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

sudo -E pip install funcsigs
sudo -E pip install unicodecsv
if [ "$1" = "${NEWTON}" -o "${RELEASE_FILE}" = "${NEWTON}" ]; then
    sudo -E pip install oslo.utils==4.1.1
    sudo -E pip install osc-lib==2.0.0
    sudo -E pip install openstacksdk==0.14.0
    sudo -E pip install oslo.cache==2.3.0
    sudo -E pip install oslo.concurrency==4.0.2
    sudo -E pip install oslo.config==7.0.0
    sudo -E pip install oslo.context==3.0.2
    sudo -E pip install oslo.db==7.0.0
    sudo -E pip install oslo.i18n==4.0.1
    sudo -E pip install oslo.log==3.45.2
    sudo -E pip install oslo.messaging==12.1.0
    sudo -E pip install oslo.middleware==4.0.2
    sudo -E pip install oslo.policy==3.1.0
    sudo -E pip install oslo.privsep==2.1.1
    sudo -E pip install oslo.reports==2.0.1
    sudo -E pip install oslo.rootwrap==6.0.2
    sudo -E pip install oslo.serialization==3.1.1
    sudo -E pip install oslo.service==2.1.1
    sudo -E pip install oslo.versionedobjects==2.0.2
elif [ "$1" = "${WALLABY}" -o "${RELEASE_FILE}" = "${WALLABY}" ]; then
    sudo -E pip install six
    sudo -E pip install openstacksdk==0.53.0
    sudo -E pip install oslo.config==8.4.0
    sudo -E pip install oslo.db==8.5.0
    sudo -E pip install oslo.log==4.3.0
    sudo -E pip install python-cinderclient==7.3.0
    sudo -E pip install ddt==1.3.1
else
    sudo -E pip install oslo.db==7.0.0
    sudo -E pip install python-cinderclient==3.5.0
    sudo -E pip install oslo.config==7.0.0
    sudo -E pip install oslo.log==3.45.2
    sudo -E pip install ddt==1.3.1
    sudo -E pip install openstacksdk==0.14.0
fi
sudo -E pip install python-novaclient/
sudo -E pip install python-openstackclient/

# Need to use older paramkio - see https://github.com/paramiko/paramiko/issues/1984
sudo -E pip install paramiko==2.7
sudo -E pip install keystoneauth1==5.0.0
