############################################################################
# 24.1 Removing unnecessary packages from the undercloud
############################################################################
# 1. Remove the unnecessary packages
sudo dnf -y remove --exclude=python-pycadf-common python2*
