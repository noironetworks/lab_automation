############################################################################
# 4.4. Setting the SSH root permission parameter on the undercloud
############################################################################
# 1. Log in to the undercloud as the stack user.
# 2. Check the /etc/ssh/sshd_config file for the PermitRootLogin parameter:
sudo grep PermitRootLogin /etc/ssh/sshd_config
# 3. If the parameter is not in the /etc/ssh/sshd_config file, edit the file and set the PermitRootLogin parameter:
# 3.1 Become root
sudo -s
# 3.2 Add line setting root login permission
echo "PermitRootLogin no" >> /etc/ssh/sshd_config
# 3.3 Exit root user
exit
