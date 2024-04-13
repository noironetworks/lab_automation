import argparse
import re


class OVSInterfaceParser(object):
    def __init__(self, outfilename='config-bridges.sh'):
        self.bridge_ports = {}
        #Matches <ofport number>(<port name>): addr:<mac address>
        self.ifmatcher = re.compile(r"^ ([0-9A-Z]{1,5})\((.*)\): addr:(.*) (.*)")
        self.cmd_script = outfilename
    def open_script_file(self):
        self.script_fd = open(self.cmd_script, "w+")
    def close_script_file(self):
        self.script_fd.close()
    def parse_ports(self, bridge_filename, prefix=None):
        fd = open(bridge_filename, 'r')
        alldata = fd.readlines()
        for idx, line in enumerate(alldata):
            line = " 10%02d" % idx + line
            groups = self.ifmatcher.match(line)
            if groups:
                if not prefix or prefix and groups[2][0:len(prefix)] == prefix:
                    self.bridge_ports[groups[2]] = {'mac': groups[3],
                                                    'ofport': groups[1],
                                                    'iface-id': groups[4]}
    def create_tap_ports(self):
        for port in self.bridge_ports.keys():
            if port[0:3] == 'tap':
                cmd = "ip tuntap add %s mode tap\n" % port
                self.script_fd.write(cmd)
                cmd = "ip link set %s address %s\n" % (port, self.bridge_ports[port]['mac'])
                self.script_fd.write(cmd)
                cmd = "ifconfig %s up\n" % port
                self.script_fd.write(cmd)
    def create_snat_ports(self):
        for port in self.bridge_ports.keys():
            if port[0:3] == 'of-':
                cmd = "ip tuntap add %s mode tap\n" % port
                self.script_fd.write(cmd)
                cmd = "ip link set %s address %s\n" % (port, self.bridge_ports[port]['mac'])
                self.script_fd.write(cmd)
                cmd = "ifconfig %s up\n" % port
                self.script_fd.write(cmd)
    def add_tap_ports(self):
        for port in self.bridge_ports.keys():
            if port[0:3] == 'tap':
                cmd = ('ovs-vsctl add-port br-int %s -- set Interface %s ofport=%s external_ids:attached-mac="%s"  external_ids:iface-id="%s"\n' %
                       (port, port, self.bridge_ports[port]['ofport'], self.bridge_ports[port]['mac'],  self.bridge_ports[port]['iface-id']))
                self.script_fd.write(cmd)
    def add_patch_ports(self):
        for port in self.bridge_ports.keys():
            if port[0:3] == 'qpf':
                patch = port.replace('qpf', 'qpi')
                cmd = ('ovs-vsctl add-port br-int %s -- set Interface %s type=patch ofport=%s mac_in_use=\\"%s\\" options:peer=%s\n' %
                        (port, port, self.bridge_ports[port]['ofport'], self.bridge_ports[port]['mac'], patch)) 
                self.script_fd.write(cmd)
                cmd = ('ovs-vsctl add-port br-fabric %s -- set Interface %s type=patch ofport=%s mac_in_use=\\"%s\\" options:peer=%s\n' %
                        (patch, patch, self.bridge_ports[patch]['ofport'], self.bridge_ports[patch]['mac'], port))
                self.script_fd.write(cmd)
            if port == 'patch-fab-ex':
                cmd = ('ovs-vsctl -- --may-exist add-port br-fabric patch-fab-ex -- set Interface patch-fab-ex type=patch ofport=%s mac_in_use=\\"%s\\" options:peer=patch-ex-fab\n' %
                (self.bridge_ports[port]['ofport'], self.bridge_ports[port]['mac']))
                self.script_fd.write(cmd)

    def add_snat_ports(self):
        for port in self.bridge_ports.keys():
            if port[0:3] == 'of-':
                cmd = ('ovs-vsctl add-port br-fabric %s -- set Interface %s ofport=%s\n' %
                        (port, port, self.bridge_ports[port]['ofport'])) 
                self.script_fd.write(cmd)

    def add_gen_ports(self):
        for port in self.bridge_ports.keys():
            if port[0:4] == 'gen2':
                cmd = ('ovs-vsctl -- --may-exist add-port br-int gen2 -- set Interface gen2 type=geneve ofport=%s mac_in_use=\\"%s\\" options:remote_ip=flow options:key=2\n' %
                (self.bridge_ports[port]['ofport'], self.bridge_ports[port]['mac']))
                self.script_fd.write(cmd)
                cmd = 'ovs-vsctl set interface gen2 ingress_policing_rate=1000\n'
                self.script_fd.write(cmd)
                cmd = 'ovs-vsctl set interface gen2 ingress_policing_burst=100\n'
                self.script_fd.write(cmd)
            if port[0:4] == 'gen1':
                cmd = ('ovs-vsctl -- --may-exist add-port br-fabric gen1 -- set interface gen1 type=geneve ofport=%s mac_in_use=\\"%s\\" options:remote_ip=flow options:key=1\n' %
                (self.bridge_ports[port]['ofport'], self.bridge_ports[port]['mac']))
                self.script_fd.write(cmd)
                cmd = ('ovs-vsctl set interface gen1 ingress_policing_rate=1000\n')
                self.script_fd.write(cmd)
                cmd = ('ovs-vsctl set interface gen1 ingress_policing_burst=100\n')
                self.script_fd.write(cmd)

    def add_vxlan_port(self):
        for port in self.bridge_ports.keys():
            if 'vxlan' in port:
                cmd = ('ovs-vsctl -- --may-exist add-port br-fabric br-fab_vxlan0 -- set Interface br-fab_vxlan0 type=vxlan ofport=%s mac_in_use=\\"%s\\" options:remote_ip=flow options:key=flow options:dst_port=8472\n' %
                (self.bridge_ports[port]['ofport'], self.bridge_ports[port]['mac']))
                self.script_fd.write(cmd)

    def create_script_file(self):
        self.open_script_file()
        self.create_tap_ports()
        self.create_snat_ports()
        self.add_tap_ports()
        self.add_patch_ports()
        self.add_snat_ports()
        self.add_gen_ports()
        self.add_vxlan_port()
        self.close_script_file()


if __name__ == '__main__':
    if_parser = OVSInterfaceParser()

    parser = argparse.ArgumentParser()
    parser.add_argument('--bridgefile', dest='bridgefiles', action='append',
                        help="File containing output from running 'ovs-ofctl show <bridge name>'")
    parser.add_argument('--outfile', dest='outfile', default='config-bridges.sh',
                        help="File containing output from running 'ovs-ofctl show <bridge name>'")

    args = parser.parse_args()
    for filename in args.bridgefiles:
        if_parser.parse_ports(filename)
    if_parser.create_script_file()
