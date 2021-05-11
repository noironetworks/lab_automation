############################################################################
# 4.5. Converting to next generation power management drivers
############################################################################
# 1. Check the current list of hardware types enabled:
source ~/stackrc
openstack baremetal driver list --type dynamic
# 2. If you use a hardware type driver that is not enabled, enable the driver using the enabled_hardware_types parameter in the undercloud.conf file
# enabled_hardware_types = ipmi,redfish,idrac
# 3. Save the file and refresh the undercloud:
# openstack undercloud install
# 4. Run the following commands, substituting the OLDDRIVER and NEWDRIVER variables for your power management type:
source ~/stackrc
OLDDRIVER="pxe_ipmitool"
NEWDRIVER="ipmi"
for NODE in $(openstack baremetal node list --driver $OLDDRIVER -c UUID -f value) ; do openstack baremetal node set $NODE --driver $NEWDRIVER; done


