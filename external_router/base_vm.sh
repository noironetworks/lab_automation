sudo apt update
sudo apt upgrade
sudo apt install sshpass
sudo apt install python3-neutronclient
sudo apt install python-is-python3
sudo apt install python3-venv


python3 -m venv .venv
. .venv/bin/activate
pip install urllib3==1.26.16
pip install rally-openstack
pip install tempest
pip install ansible
HTTPS_PROXY=http://proxy.esl.cisco.com:80/ ansible-galaxy collection install openstack.cloud
HTTPS_PROXY=http://proxy.esl.cisco.com:80/ ansible-galaxy collection install community.general
pip install python-tempestconf
