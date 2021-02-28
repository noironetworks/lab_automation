#!/bin/bash
# Host name contains the FAB number
FAB_NO=`hostname | cut -d "-" -f 1 | cut -b 4-`
# Assumes eth0 is the management IP of the external router, and /24 subnet
EXT_RTR_IP=`ip -o -4 addr | grep eth0 | awk '{print $4}' | awk -F'/' '{print $1}'`
EXT_RTR_NET=`echo ${EXT_RTR_IP} | cut -d'.' -f1-3`".0"
NOIRO_CTRLR_IP=172.28.184.8

# Be sure you have a good reason for changing these
# two environment variables
NOVACLIENT_VERSION=stable/ocata

# Supported releases
NEWTON="newton"
OCATA="ocata"
PIKE="pike"
QUEENS="queens"
TRAIN="train"
RELEASES="${NEWTON} ${OCATA} ${PIKE} ${QUEENS} ${TRAIN}"
DIRECTOR="director"
JUJU="juju"

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
    NEUTRON_GIT_HASH="stable/pike"
elif [ "$1" = "${QUEENS}" -o "${RELEASE_FILE}" = "${QUEENS}" ]; then
    RELEASE="stable/queens"
    TEMPEST_VERSION="19.0.0"
    NEUTRON_TEMPEST_VERSION="0.5.0"
    NEUTRON_GIT_HASH="stable/queens"
elif [ "$1" = "${TRAIN}" -o "${RELEASE_FILE}" = "${TRAIN}" ]; then
    RELEASE="stable/train"
    TEMPEST_VERSION="21.0.0"
    NEUTRON_TEMPEST_VERSION="0.5.0"
    NEUTRON_GIT_HASH="stable/train"
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
sudo -E apt-get update

# We need python2.7 for OpenStack
sudo -E apt-get -y --allow-unauthenticated install python2.7
sudo -E apt-get -y --allow-unauthenticated install sshpass
sudo -E apt-get -y --allow-unauthenticated install git


if [ "${UNDERCLOUD_TYPE}" = "${DIRECTOR}" ]; then
    RCFILE='overcloudrc'
    UNDERCLOUD_USER="stack"
else
    RCFILE='admin-openrc.sh'
    UNDERCLOUD_USER="noiro"
fi

# We need keypairs
ssh-keygen -b 2048 -t rsa -f ~/.ssh/id_rsa -q -N ""

# Add ourselves to the undercloud authorized hosts
cat ~/.ssh/id_rsa.pub | sshpass -p noir0123 ssh -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP} "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
sshpass -p noir0123 ssh -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP} "chmod 700 .ssh; chmod 640 .ssh/authorized_keys"

if [ "${UNDERCLOUD_TYPE}" = "${DIRECTOR}" ]; then
    # Set up passwordless access to the openstack controller
    KEY=`cat ~/.ssh/id_rsa.pub`
    echo "CTRL_IP=\`source stackrc && nova list | grep controller | awk -F'|' '{print \$7}' | cut -c11-\`" > test.sh
    echo "for CIP in \$CTRL_IP; do" >> test.sh
    echo -n "ssh -o StrictHostKeyChecking=no heat-admin@\$CIP " >> test.sh
    echo "\"echo $KEY >> .ssh/authorized_keys\"" >> test.sh
    echo "done" >> test.sh
    
    scp -o StrictHostKeyChecking=no test.sh ${UNDERCLOUD_USER}@${UNDERCLOUD_IP}:~/
    ssh -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP} "chmod +x test.sh"
    ssh -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP} "./test.sh"
fi


scp -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP}:~/${RCFILE}* .
CTRLR_REST_IP=`egrep OS_AUTH_URL ${RCFILE} | awk -F'/' '{print $3}' | awk -F ':' '{print $1}'`

# Set up env vars for configuration
#GW1_IP=`printf "1.1%02d.1.254" ${FAB_NO}`
#GW2_IP=`printf "1.1%02d.2.254" ${FAB_NO}`
#EXT1_IP=`printf "1.1%02d.1.1" ${FAB_NO}`
#EXT2_IP=`printf "1.1%02d.2.1" ${FAB_NO}`

GW1_IP='1.250.1.254'
GW2_IP='1.251.1.254'
EXT1_IP='1.250.1.1'
EXT2_IP='1.251.1.1'

if [ "${UNDERCLOUD_TYPE}" = "${DIRECTOR}" ]; then
    CLOUD_NET='1.100.1.0'
    CLOUD_GATEWAY=${CTRLR_REST_IP}
else
    CLOUD_NET='1.11.1.0'
    CLOUD_GATEWAY=${UNDERCLOUD_IP}
fi

# Environment vars to let us access stuff
HTTP_PROXY='http://proxy.esl.cisco.com:80'
HTTP_PROXY_STRING="http_proxy=${HTTP_PROXY}"
HTTPS_PROXY_STRING="https_proxy=${HTTP_PROXY}"
NO_PROXY_STRING="no_proxy=127.0.0.1,localhost,${EXT_RTR_IP},${CLOUD_GATEWAY},${EXT_RTR_NET}/24,${CLOUD_NET}/24,${NOIRO_CTRLR_IP}"
export ${HTTP_PROXY_STRING}
export ${HTTPS_PROXY_STRING}
export ${NO_PROXY_STRING}
export PYTHONPATH=/home/noiro/noirotest
echo "export ${HTTP_PROXY_STRING}" >> .bashrc
echo "export ${HTTPS_PROXY_STRING}" >> .bashrc
echo "export ${NO_PROXY_STRING}" >> .bashrc
echo "export PYTHONPATH=/home/noiro/noirotest" >> .bashrc


# Set up route to allow access to director internal IPs
# (note: this is needed so we can get the keystone IP below)
sudo route add -net ${CLOUD_NET} netmask 255.255.255.0 gateway ${CLOUD_GATEWAY}

if [ "${UNDERCLOUD_TYPE}" = "${DIRECTOR}" ]; then
    # Set up env vars for access
    CTRLR_INT_IP=`ssh -o StrictHostKeyChecking=no ${UNDERCLOUD_USER}@${UNDERCLOUD_IP} "source stackrc && nova list | grep controller" | awk -F'|' '{print $7}' | cut -c11- | tr -d '[:space:]'`
    KEYSTONE_IP=`ssh -o StrictHostKeyChecking=no heat-admin@${CTRLR_INT_IP} "sudo egrep auth_url /etc/neutron/neutron.conf"  | grep v3 | awk -F':' '{print $2}' | cut -c3-`
    ssh -o StrictHostKeyChecking=no heat-admin@${CTRLR_INT_IP} "sudo cp ~/${RCFILE} /root/" >> /dev/null
    # Establish ssh logins
    ssh -o StrictHostKeyChecking=no heat-admin@${CTRLR_REST_IP} ls >> /dev/null
    ssh -o StrictHostKeyChecking=no heat-admin@${CTRLR_INT_IP} ls >> /dev/null
    scp -o StrictHostKeyChecking=no ~/${RCFILE}* heat-admin@${CTRLR_INT_IP}:~/
fi


# Install pip
sudo -E apt-get -y --allow-unauthenticated update
sudo -E apt -y --allow-unauthenticated install python-pip
sudo -E pip install pip==20.3.4
# Install packages from pip repositories
sudo -E pip install fabric==1.14.0  # newer versions break our code
sudo -E pip install ddt
sudo -E pip install click
sudo -E pip install testscenarios
sudo -E apt -y --allow-unauthenticated install python-os-testr
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
    cd $repo && git checkout ${RELEASE} && cd
done
if [ "$1" = "${QUEENS}" ] || [ "${RELEASE_FILE}" = "${QUEENS}" ] || [ "$1" = "${TRAIN}" ] || [ "${RELEASE_FILE}" = "${TRAIN}" ]; then
    ${GIT_CLONE}/openstack/neutron-tempest-plugin.git
    cd neutron-tempest-plugin && git checkout $NEUTRON_TEMPEST_VERSION && cd
fi
python exclude_tests.py --undercloud-type ${UNDERCLOUD_TYPE}
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

# remaining repos use the release under test
REPOS="python-openstackclient python-neutronclient"
for repo in $REPOS; do
    sudo -E pip install $repo/
done
sudo -E pip install neutron/
if [ "$1" = "${QUEENS}" -o "${RELEASE_FILE}" = "${QUEENS}" -o "$1" = "${TRAIN}" -o "${RELEASE_FILE}" = "${TRAIN}" ]; then
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
wget https://download.cirros-cloud.net/0.3.5/cirros-0.3.5-x86_64-disk.img
wget http://${NOIRO_CTRLR_IP}/images/ubuntu_multi_nics.qcow2
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
ssh -o StrictHostKeyChecking=no noiro@${EXT_RTR_IP} ls >> /dev/null

# Set up config file for noirotest
cp ~/noirotest/testcases/f${FAB_NO}-director.yaml ~/noirotest/testcases/testconfig.yaml

if [ "${UNDERCLOUD_TYPE}" = "${DIRECTOR}" ]; then
    sed -i "s/controller_ip:.*/controller_ip: \"$CTRLR_REST_IP\"/g" ~/noirotest/testcases/testconfig.yaml
    sed -i "s/network_node:.*/network_node: \"$CTRLR_INT_IP\"/g" ~/noirotest/testcases/testconfig.yaml
    sed -i "s/keystone_ip:.*/keystone_ip: \"$KEYSTONE_IP\"/g" ~/noirotest/testcases/testconfig.yaml
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
wget -q -O- https://raw.githubusercontent.com/noironetworks/rally/noiro-master/install_rally.sh > install_rally.sh
# Get rid of question
sed -i 's/ask_yn "Proceed with installation anyway?"/true/g' ~/install_rally.sh
sed -i 's/bootstrap.pypa.io/bootstrap.pypa.io\/2.7/g' ~/install_rally.sh
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
cd python-novaclient && git checkout $NOVACLIENT_VERSION && cd
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
if [ "$1" = "${QUEENS}" -o "${RELEASE_FILE}" = "${QUEENS}" -o "$1" = "${TRAIN}" -o "${RELEASE_FILE}" = "${TRAIN}" ]; then
    AIM_CONF=${QUEENS_PREFIX}/aim${AIM_CONF}
    NEUTRON_CONF=${QUEENS_PREFIX}/neutron${NEUTRON_CONF}
    PLUGIN_CONF=${QUEENS_PREFIX}/neutron${PLUGIN_CONF}
    RESTART_CMD='sudo docker restart '
    NEUTRON_SERVICE='neutron_api'
    AIM_SERVICE='ciscoaci_aim'
    AIM_CMD_PREFIX="sudo docker exec -u root ${AIM_SERVICE} "
    SILENCE=""
fi
if [ "${UNDERCLOUD_TYPE}" = "${DIRECTOR}" ]; then
    if [ "$1" != "${QUEENS}" -o "$1" = "${TRAIN}" ]; then
        ssh -o StrictHostKeyChecking=no heat-admin@${CTRLR_INT_IP} "sudo sed -i 's/#dns_domain.*/dns_domain=localdomain/g' ${NEUTRON_CONF}" >> /dev/null
    fi
    ssh -o StrictHostKeyChecking=no heat-admin@${CTRLR_INT_IP} "sudo sed -i 's/extension_drivers=apic_aim,port_security/extension_drivers=apic_aim,port_security,dns/g' ${PLUGIN_CONF}" >> /dev/null
    if [ "$1" = "${NEWTON}" -o "${RELEASE_FILE}" = "${NEWTON}" ]; then
        ssh -o StrictHostKeyChecking=no heat-admin@${CTRLR_INT_IP} "sudo sed -i 's/global_physnet_mtu=1496/#global_physnet_mtu=1496/g' ${NEUTRON_CONF}" >> /dev/null
    fi
    ssh -o StrictHostKeyChecking=no heat-admin@${CTRLR_INT_IP} "${RESTART_CMD} ${NEUTRON_SERVICE}" >> /dev/null
    ssh -o StrictHostKeyChecking=no heat-admin@${CTRLR_INT_IP} "sudo head -n -2 ${AIM_CONF} > ~/aimctl.conf" >> /dev/null
    ssh -o StrictHostKeyChecking=no heat-admin@${CTRLR_INT_IP} "sudo mv ~/aimctl.conf ${AIM_CONF}" >> /dev/null
    if [ "$1" = "${QUEENS}" -o "${RELEASE_FILE}" = "${QUEENS}" -o "$1" = "${TRAIN}" -o "${RELEASE_FILE}" = "${TRAIN}" ]; then
        ssh -o StrictHostKeyChecking=no heat-admin@${CTRLR_INT_IP} "${RESTART_CMD} ${AIM_SERVICE}" >> /dev/null
    fi
    ssh -o StrictHostKeyChecking=no heat-admin@${CTRLR_INT_IP} "${AIM_CMD_PREFIX} aimctl manager host-domain-mapping-v2-delete '*' pdom_physnet1 PhysDom" >> /dev/null
    ssh -o StrictHostKeyChecking=no heat-admin@${CTRLR_INT_IP} "${AIM_CMD_PREFIX} aimctl manager physical-domain-delete pdom_physnet1" >> /dev/null
    ssh -o StrictHostKeyChecking=no heat-admin@${CTRLR_INT_IP} "${AIM_CMD_PREFIX} aimctl manager load-domains" >> /dev/null
fi
sudo -E pip install funcsigs
sudo -E pip install unicodecsv
sudo -E pip install oslo.db==7.0.0
sudo -E pip install python-cinderclient==3.5.0
sudo -E pip install python-openstackclient/
sudo -E pip install oslo.config==7.0.0
sudo -E pip install oslo.log==3.45.2
sudo -E pip install python-novaclient/
sudo -E pip install ddt==1.3.1
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
fi
