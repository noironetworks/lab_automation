#### Script for creating exetrtr base VM ####
#
# Please make sure proxy for apt is configured by creating file
# /etc/apt/apt.conf.d/99proxy  with content
# Acquire {
#   HTTP::proxy "http://proxy.esl.cisco.com:80/";
#   HTTPS::proxy "http://proxy.esl.cisco.com:80/";
# }
#
#

sudo apt update
sudo apt -y upgrade
sudo apt install -y sshpass
sudo apt install -y python3-neutronclient
sudo apt install -y python-is-python3
sudo apt install -y python3-pip
sudo apt install -y python3-venv

export HTTPS_PROXY=http://proxy.esl.cisco.com:80/
export HTTP_PROXY=http://proxy.esl.cisco.com:80/
export https_proxy=http://proxy.esl.cisco.com:80/
export http_proxy=http://proxy.esl.cisco.com:80/

python3 -m venv .venv
. .venv/bin/activate
pip install urllib3==1.26.16
pip install rally-openstack
pip install tempest
pip install ansible
ansible-galaxy collection install openstack.cloud
ansible-galaxy collection install community.general
pip install python-tempestconf
