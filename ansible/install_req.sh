#!/usr/bin/env bash

sudo -E apt-get -y --allow-unauthenticated install python2.7
sudo -E apt-get -y --allow-unauthenticated install sshpass

HTTP_PROXY='http://proxy.esl.cisco.com:80'
HTTP_PROXY_STRING="http_proxy=${HTTP_PROXY}"
HTTPS_PROXY_STRING="https_proxy=${HTTP_PROXY}"
NO_PROXY_STRING="no_proxy=127.0.0.1,localhost,10.30.120.119"
export ${HTTP_PROXY_STRING}
export ${HTTPS_PROXY_STRING}
export ${NO_PROXY_STRING}
export PYTHONPATH=/home/noiro/noirotest
echo "export ${HTTP_PROXY_STRING}" >> .bashrc
echo "export ${HTTPS_PROXY_STRING}" >> .bashrc
echo "export ${NO_PROXY_STRING}" >> .bashrc
echo "export PYTHONPATH=/home/noiro/noirotest" >> .bashrc

sudo -E apt-get -y --allow-unauthenticated update
sudo -E apt -y --allow-unauthenticated install python-pip
sudo -E pip install pip==20.3.4


echo 'Install Ansible Dependencies'
sudo apt-get install -y python-setuptools
#sudo easy_install jinja2
#sudo easy_install pyyaml
#sudo easy_install paramiko

export ${HTTP_PROXY_STRING}
export ${HTTPS_PROXY_STRING}
export ${NO_PROXY_STRING}


echo 'Install Ansible'
pip install ansible

echo 'Check Ansible Version'
ansible --version

echo 'Prerequisites'
sudo apt-get -y update
sudo apt-get -y install build-essential checkinstall
sudo apt-get -y install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
