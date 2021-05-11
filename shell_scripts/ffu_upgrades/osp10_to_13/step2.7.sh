##################################################
# 2.7. REBOOTING CONTROLLER AND COMPOSABLE NODES
##################################################

# 1. Log in to the node that you want to reboot
# 2. Optional: If the node uses Pacemaker resources, stop the cluster
#    (The --force is needed when there is only one controller?)
sudo pcs cluster stop --force
# 3. . Reboot the node:
sudo reboot
# 4. Wait until the node boots
# 5. Check the services
# 5a. If the node uses Pacemaker services, check that the node has rejoined the cluster
sudo pcs status
# 5b. If the node uses Systemd services, check that all services are enabled
sudo systemctl status
# 5c. Repeat these steps for all Controller and composable nodes

