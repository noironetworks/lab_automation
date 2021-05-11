######################################################
# 2.2 BACKING UP THE OVERCLOUD CONTROL PLANE SERVICES
######################################################

# 1 Perform the database backup
## 1a. Log into a Controller node
NODE=$(openstack server list --name controller-0 -f value -c Networks | cut -d= -f2); ssh heat-admin@$NODE
## 1b. Change to the root user
sudo -i
## 1c. Create a temporary directory to store the backups:
mkdir -p /var/tmp/mysql_backup/
## 1d. Obtain the database password and store it in the MYSQLDBPASS environment variable.
MYSQLDBPASS=$(sudo hiera -c /etc/puppet/hiera.yaml mysql::server::root_password)
## 1e. Backup the database
mysql -uroot -p$MYSQLDBPASS -s -N -e "select distinct table_schema from information_schema.tables where engine='innodb' and table_schema != 'mysql';" | xargs mysqldump -uroot -p$MYSQLDBPASS --single-transaction --databases > /var/tmp/mysql_backup/openstack_databases-`date +%F`-`date +%T`.sql
## 1f. Backup all the users and permissions information
mysql -uroot -p$MYSQLDBPASS -s -N -e "SELECT CONCAT('\"SHOW GRANTS FOR ''',user,'''@''',host,''';\"') FROM mysql.user where (length(user) > 0 and user NOT LIKE 'root')" | xargs -n1 mysql -uroot -p$MYSQLDBPASS -s -N -e | sed 's/$/;/' > /var/tmp/mysql_backup/openstack_databases_grants-`date +%F`-`date +%T`.sql

# 2 Backup the Pacemaker configuration
## 2a. Log into a Controller node
## 2b. Run the following command to create an archive of the current Pacemaker configuration:
sudo pcs config backup pacemaker_controller_backup
## 2c. Copy the resulting archive (pacemaker_controller_backup.tar.bz2) to a secure location

# 3 Backup the OpenStack Telemetry database
## 3a. Connect to any controller and get the IP of the MongoDB primary instance
MONGOIP=$(sudo hiera -c /etc/puppet/hiera.yaml mongodb::server::bind_ip)
## 3b. Create the backup:
mkdir -p /var/tmp/mongo_backup/
mongodump --oplog --host $MONGOIP --out /var/tmp/mongo_backup/
## 3c. Copy the database dump in /var/tmp/mongo_backup/ to a secure location

# 4 Backup the Redis cluster
## 4a. Obtain the Redis endpoint from HAProxy
REDISIP=$(sudo hiera -c /etc/puppet/hiera.yaml redis_vip)
## 4b. Obtain the master password for the Redis cluster
REDISPASS=$(sudo hiera -c /etc/puppet/hiera.yaml redis::masterauth)
## 4c. Check connectivity to the Redis cluster
redis-cli -a $REDISPASS -h $REDISIP ping
## 4d. Dump the Redis database
redis-cli -a $REDISPASS -h $REDISIP bgsave

# 5 Backup the filesystem on each Controller node
## 5a. Create a directory for the backup:
mkdir -p /var/tmp/filesystem_backup/
## 5b. Run the following tar command
tar --acls --ignore-failed-read --xattrs --xattrs-include='*.*' \
    -zcvf /var/tmp/filesystem_backup/`hostname`-filesystem-`date '+%Y-%m-%d-%H-%M-%S'`.tar \
    /etc \
    /srv/node \
    /var/log \
    /var/lib/nova \
    --exclude /var/lib/nova/instances \
    /var/lib/glance \
    /var/lib/keystone \
    /var/lib/cinder \
    /var/lib/heat \
    /var/lib/heat-config \
    /var/lib/heat-cfntools \
    /var/lib/rabbitmq \
    /var/lib/neutron \
    /var/lib/haproxy \
    /var/lib/openvswitch \
    /var/lib/redis \
    /var/lib/os-collect-config \
    /usr/libexec/os-apply-config \
    /usr/libexec/os-refresh-config \
    /home/heat-admin
## 5c. Copy the resulting tar file to a secure location

