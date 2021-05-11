################################################
# 2.1. CREATING A BAREMETAL UNDERCLOUD BACKUP
################################################

# 1. Log into the undercloud as the root user
if [ "$(whoami)" != "root" ]; then
    echo "You're not root!"
    exit 0
fi
# 2. Back up the database
mysqldump --opt --all-databases > /root/undercloud-all-databases.sql
# 3. Create a backup directory and change the user ownership of the directory to the stack user
mkdir /backup
chown stack: /backup
# 4. Change to the backup directory
cd /backup
# 5. Archive the database backup and the configuration files
tar --xattrs --xattrs-include='*.*' --ignore-failed-read -cf \
    undercloud-backup-`date +%F`.tar \
    /root/undercloud-all-databases.sql \
    /etc \
    /var/log \
    /var/lib/glance \
    /var/lib/certmonger \
    /var/lib/docker \
    /var/lib/registry \
    /srv/node \
    /root \
    /home/stack
