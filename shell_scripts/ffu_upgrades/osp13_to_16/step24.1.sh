############################################################################
# 24.1 Removing unnecessary packages from the undercloud
############################################################################
# 1. Remove the unnecessary packages
sudo dnf -y remove --exclude=python-pycadf-common python2*
# 2. Remove the content from the /httpboot and /tftpboot directories that includes old images used in Red Hat OpenStack 13:
sudo rm -rf /httpboot /tftpboot
