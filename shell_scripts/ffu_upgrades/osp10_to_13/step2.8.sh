###############################################
# 2.8. REBOOTING A CEPH STORAGE (OSD) CLUSTER
###############################################

# 1. Log in to a Ceph MON or Controller node and disable Ceph Storage cluster rebalancing
#    temporarily
sudo ceph osd set noout
sudo ceph osd set norebalance
# 2. Select the first Ceph Storage node to reboot and log into it
# 3. Reboot the node
sudo reboot
# 4. Wait until the node boots
# 5. Log in to the node and check the cluster status
sudo ceph -s
# 6. Log out of the node, reboot the next node, and check its status. Repeat this process until you
#    have rebooted all Ceph storage nodes.
# 7. When complete, log into a Ceph MON or Controller node and enable cluster rebalancing again
sudo ceph osd unset noout
sudo ceph osd unset norebalance
# 8. Perform a final status check to verify the cluster reports HEALTH_OK
sudo ceph status
