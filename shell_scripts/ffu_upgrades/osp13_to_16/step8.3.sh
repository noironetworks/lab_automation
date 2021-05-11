############################################################################
# 8.3 Copying the Leapp data to the overcloud nodes
############################################################################
# 1. Log in to the undercloud as the stack user.
# 2. Check the /etc/leapp/files directory on the undercloud:
if [[ "$(sudo ls /etc/leapp/files/ | grep "pes-events.json\|repomap.csv" | wc -l)" -ne "2" ]]; then
    echo "Invalid LEAPP configuration."
fi
