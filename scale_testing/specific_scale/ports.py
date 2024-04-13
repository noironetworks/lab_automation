from collections import deque
import argparse
import re
import subprocess


CMD_TIME_WAIT=30
DIRECTOR_RC = 'overcloudrc'

DIRECTOR = 'director'
ROUTER = 'router'

class OVSPortScriptGenerator(object):
    """Script file generator for OVS

    Generate a shell script to create virtual (TAP) pports,
    and attach them to an OVS bridge. The information used
    to create the script 

    """
    def __init__(self, cloud_ip, tenant, hosts_file, max_per_host):
        self.cloud_ip = cloud_ip
        self.tenant = tenant
        self.hosts_file = hosts_file
        self.max_per_host = max_per_host

        self.bind_ports_filename = 'bind-ports.sh'
        self.bridge_ports = {}
        self.fds_by_host = {}
        self.bind_ports_fd = None
        self.hosts = deque()
        self.undercloud_type = ROUTER
        if self.undercloud_type == DIRECTOR:
            #self.cli_host = self.controller_host
            #self.cli_user = 'heat-admin'
            self.KEY = 'source ~/' + DIRECTOR_RC + ' && '
        elif self.undercloud_type == ROUTER:
            #self.cli_host = self.external_router
            #self.cli_user = 'noiro'
            self.KEY = 'source ~/' + DIRECTOR_RC + ' && '
        else:
            print("Unsupported undercloud type: " + undercloud_type)

    def open_script_files(self):
        with open(self.hosts_file, "r") as fd:
            self.bind_ports_fd = open(self.bind_ports_filename, 'w+')
            hosts = fd.readlines()
            for host in hosts:
                hostname = host.strip('\n')
                self.hosts.append(hostname)
                fd_dict = self.fds_by_host.setdefault(hostname, {'create': None, 'delete': None})
                fd_dict['create'] = open('create-ports-' + hostname + '.sh', 'w+')
                fd_dict['delete'] = open('delete-ports-' + hostname + '.sh', 'w+')
                self.fds_by_host[hostname].update(fd_dict)

    def parse_ports(self, prefix=None):
        for idx, line in enumerate(self.port_info):
            uuid, mac = line.split()
            iface_id = uuid
            ofport = str(idx + 1000)
            tap_name = 'tap' + uuid[:11]
            self.bridge_ports[tap_name] = {'mac': mac,
                                           'ofport': ofport,
                                           'iface-id': iface_id}

    def generate_script_files(self):
        for idx, port in enumerate(self.bridge_ports.keys()):
            current_host = self.hosts[0]
            self.hosts.rotate()
            create_fd = self.fds_by_host[current_host]['create']
            delete_fd = self.fds_by_host[current_host]['delete']
            uuid = self.bridge_ports[port]['iface-id']
            cmd = "neutron port-update --binding:host_id=%(host)s %(port_id)s\n" % {
                    'host': current_host,
                    'port_id': uuid
                   }
            self.bind_ports_fd.write(cmd)
            if idx < int(self.max_per_host)*len(self.hosts):
                continue
            # Create commands
            cmd = "ip tuntap add %s mode tap\n" % port
            create_fd.write(cmd)
            cmd = "ip link set %s address %s\n" % (port, self.bridge_ports[port]['mac'])
            create_fd.write(cmd)
            cmd = "ifconfig %s up\n" % port
            create_fd.write(cmd)
            mac = self.bridge_ports[port]['mac'].replace("fe:", "fa:")
            cmd = ('ovs-vsctl add-port br-int %s -- set Interface %s ofport=%s external_ids:attached-mac="%s"  external_ids:iface-id="%s"\n' %
                   (port, port, self.bridge_ports[port]['ofport'], mac,  self.bridge_ports[port]['iface-id']))
            create_fd.write(cmd)

            # Delete commands
            cmd = ('ovs-vsctl del-port br-int %s\n' % port)
            delete_fd.write(cmd)
            cmd = "ip link del %s\n" % port
            delete_fd.write(cmd)
            cmd = "ip tuntap del %s mode tap\n" % port
            delete_fd.write(cmd)

    def local_command(self, command):
        cmd = self.KEY + command
        print(cmd)
        result_string = subprocess.check_output(['bash','-c', cmd]).decode('utf-8')
        result_list = [result.strip()
                       for result in result_string.split("\n") if result]
        return result_list

    def get_vm_ports(self, tenant, az='nova', port_filter=None):
        owner_filter = "compute:%s" % az
        self.port_info = self.get_ports(tenant, owner_filter=owner_filter, port_filter=port_filter)

    def get_ports(self, tenant, owner_filter=None, port_filter=None):
        """Get ports matching a certain criteria

        Get all the VM ports (device_owner start with the compute: prefix)
        for a given project
        """
        cmd = 'openstack port list '
        cmd += '--project %s ' % tenant
        cmd += '--device-owner %s -c ID -f value -c "MAC Address" -f value' % owner_filter
        if port_filter:
            cmd += ' ' + port_filter
        port_info = []
        try:
            port_info = self.local_command(cmd)
        except subprocess.CalledProcessError as e:
            print("Error from command: %s" % e)
        return port_info


def run():
    parser = argparse.ArgumentParser(description='Port manager')
    parser.add_argument('--cloud-ip',default="10.30.120.201",
                         help='IP Address of OpenStack horizon.')
    parser.add_argument('--tenant',default='admin',
                         help='Tenant name or UUID')
    parser.add_argument('--az',default='nova',
                         help='availiability zone name')
    parser.add_argument('--port-filter', default=None,
                         help='Additional string to use for port filtering')
    parser.add_argument('--max-per-host', default=None,
                         help='Maximum ports to create on a host with scripts.')
    parser.add_argument('--ports-file', default=None,
                         help='File containing list of ports to bind.')
    parser.add_argument('--hosts-file', default=None,
                         help='File containing list of hosts to bind ports to (one hostname per line).')
    args = parser.parse_args()
    script_generator = OVSPortScriptGenerator(args.cloud_ip, args.tenant, args.hosts_file, args.max_per_host)
    script_generator.open_script_files()
    script_generator.get_vm_ports(args.tenant, az=args.az, port_filter=args.port_filter)
    script_generator.parse_ports()
    script_generator.generate_script_files()

if __name__ == '__main__':
    run()
