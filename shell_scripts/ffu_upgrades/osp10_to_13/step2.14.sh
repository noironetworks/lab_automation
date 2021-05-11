#############################
# 2.14. RETAINING YUM HISTORY
##############################

# 1. On each node, run the following command to save the entire yum history of the node in a file
sudo yum history list all > /home/heat-admin/$(hostname)-yum-history-all
# 2. On each node, run the following command to save the ID of the last yum history item
yum history list all | head -n 5 | tail -n 1 | awk '{print $1}' > /home/heat-admin/$(hostname)-yum-history-all-last-id
# 3. Copy these files to a secure location
