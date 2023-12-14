#!/usr/bin/python

import click
import datetime
import logging as log
import os
import paramiko
import subprocess
import sys
import time
import uuid

from cleanup_tempest import cleanup_tempest
import tempest_conf as cfg_template

JUJU='juju'
DIRECTOR='director'
JUJU_RC='admin-openrc.sh'
DIRECTOR_RC='overcloudrc'
PPATH='export PYTHONPATH=/home/noiro/noirotest && '
CMD_TIME_WAIT = 15
with open('fab_name.txt') as f:
    sysid = f.readline().strip()
#O FIXME: we should fix these in the DB, but for now,
# this will have to do.
L3OUT_MAP= {
    'fab6': {
        'prefix': 'sauto_fab6'
        },
    'fab8': {
        'prefix': 'sauto_fab8'
        },
    'k8s-bm-1': {
        'prefix': 'sauto_k8s-bm-1'
        },
    'ostack-bm-1': {
        'prefix': 'sauto'
        },
    'ostack-bm-2': {
        'prefix': 'sauto'
        },
    'ostack-bm-3': {
        'prefix': 'os-bm-3'
        },
    'ostack-pt-1': {
        'prefix': 'os-pt-1'
        },
    'ostack-pt-1-s1': {
        'prefix': 'os-pt-1-s1'
        },
    'opflex-pt-1': {
        'prefix': 'opflex-pt-1'
        },
    'opflex-pt-1-s1': {
        'prefix': 'opflex-pt-1-s1'
        },
    'opflex-pt-2': {
        'prefix': 'opflex-pt-2'
        },
    'opflex-pt-2-s1': {
        'prefix': 'opflex-pt-2-s1'
        },
    'fab201': {
        'prefix': 'sauto'
        }
    }
FAB_NAME = L3OUT_MAP[sysid]['prefix']
# Wait 3 hours max
TEMPEST_WAIT_TIME = (60*60*3)
NOIRO_SETUP_WAIT_TIME = (60*2)
ML2_SANITY_WAIT_TIME = (60*30)
GBP_SANITY_WAIT_TIME = (60*30)
EAST_WEST_WAIT_TIME = (60*45)
NORTH_SOUTH_WAIT_TIME = (60*60)
CLEAR_IP_TABLES_RULE='iptables -D INPUT -j REJECT --reject-with icmp-host-prohibited'
default_password = 'noir0123'
TESTR_DOT_CONF="""
[DEFAULT]
test_command=OS_STDOUT_CAPTURE=${OS_STDOUT_CAPTURE:-1} \
    OS_STDERR_CAPTURE=${OS_STDERR_CAPTURE:-1} \
    OS_TEST_TIMEOUT=${OS_TEST_TIMEOUT:-500} \
    ${PYTHON:-python} -m subunit.run discover -t /usr/local/lib/python2.7/dist-packages/tempest /usr/local/lib/python2.7/dist-packages/tempest/test_discover $LISTOPT $IDOPTION
test_id_option=--load-list $IDFILE
test_list_option=--list
group_regex=([^\.]*\.)*
"""


# Dictionary that shows which tempest tests to exclude, by release
excluded_test_matrix = {
    'stable/newton': [
        ('tempest.api.network.test_floating_ips.FloatingIPTestJSON.test_floating_ip_update_different_router',
         'Test uses overlapping CIDRs in the same VRF'),
        ('tempest.api.network.test_networks.NetworksTest.test_external_network_visibility',
         'BUG: https://github.com/noironetworks/support/issues/916'),
        ('tempest.api.network.test_security_groups.SecGroupTest.test_create_show_delete_security_group_rule',
         'BUG: https://github.com/noironetworks/support/issues/710'),
        ('tempest.scenario.test_network_basic_ops.TestNetworkBasicOps.test_subnet_details',
         "BIG: https://github.com/noironetworks/support/issues/915"),
        ('tempest.scenario.test_network_basic_ops.TestNetworkBasicOps.test_update_router_admin_state',
         'BUG: https://github.com/noironetworks/support/issues/491'),
        ('neutron.tests.tempest.api.test_floating_ips_negative.FloatingIPNegativeTestJSON.test_associate_floatingip_with_port_with_floatingip',
         'Test uses overlapping CIDRs in the same VRF'),
        ('neutron.tests.tempest.api.test_timestamp.TestTimeStampWithSecurityGroup.test_create_sg_with_timestamp',
         'BUG: https://github.com/noironetworks/support/issues/710'),
        ('neutron.tests.tempest.api.test_timestamp.TestTimeStampWithSecurityGroup.test_create_sgrule_with_timestamp',
         'BUG: https://github.com/noironetworks/support/issues/710'),
        ('neutron.tests.tempest.api.test_timestamp.TestTimeStampWithSecurityGroup.test_show_sg_attribute_with_timestamp',
         'BUG: https://github.com/noironetworks/support/issues/710'),
        ('neutron.tests.tempest.api.test_timestamp.TestTimeStampWithSecurityGroup.test_show_sgrule_attribute_with_timestamp',
         'BUG: https://github.com/noironetworks/support/issues/710'),
        ('neutron.tests.tempest.api.test_timestamp.TestTimeStampWithSecurityGroup.test_update_sg_with_timestamp',
         'BUG: https://github.com/noironetworks/support/issues/710')
    ],
    'stable/ocata': [
        ('tempest.api.network.test_floating_ips.FloatingIPTestJSON.test_floating_ip_update_different_router',
         'Test uses overlapping CIDRs in the same VRF'),
        ('tempest.api.network.test_networks.NetworksTest.test_external_network_visibility',
         'BUG: https://github.com/noironetworks/support/issues/916'),
        ('tempest.api.network.test_security_groups.SecGroupTest.test_create_show_delete_security_group_rule',
         'BUG: https://github.com/noironetworks/support/issues/710'),
        ('tempest.scenario.test_network_basic_ops.TestNetworkBasicOps.test_subnet_details',
         "BIG: https://github.com/noironetworks/support/issues/915"),
        ('tempest.scenario.test_network_basic_ops.TestNetworkBasicOps.test_update_router_admin_state',
         'BUG: https://github.com/noironetworks/support/issues/491'),
        ('neutron.tests.tempest.api.test_floating_ips_negative.FloatingIPNegativeTestJSON.test_associate_floatingip_with_port_with_floatingip',
         'Test uses overlapping CIDRs in the same VRF'),
        ('neutron.tests.tempest.api.test_timestamp.TestTimeStampWithSecurityGroup.test_create_sg_with_timestamp',
         'BUG: https://github.com/noironetworks/support/issues/710'),
        ('neutron.tests.tempest.api.test_timestamp.TestTimeStampWithSecurityGroup.test_create_sgrule_with_timestamp',
         'BUG: https://github.com/noironetworks/support/issues/710'),
        ('neutron.tests.tempest.api.test_timestamp.TestTimeStampWithSecurityGroup.test_show_sg_attribute_with_timestamp',
         'BUG: https://github.com/noironetworks/support/issues/710'),
        ('neutron.tests.tempest.api.test_timestamp.TestTimeStampWithSecurityGroup.test_show_sgrule_attribute_with_timestamp',
         'BUG: https://github.com/noironetworks/support/issues/710'),
        ('neutron.tests.tempest.api.test_timestamp.TestTimeStampWithSecurityGroup.test_update_sg_with_timestamp',
         'BUG: https://github.com/noironetworks/support/issues/710')
    ],
    'stable/pike': [
        ('tempest.api.network.test_floating_ips.FloatingIPTestJSON.test_floating_ip_update_different_router',
         'Test uses overlapping CIDRs in the same VRF'),
        ('tempest.api.network.test_networks.NetworksTest.test_external_network_visibility',
         'BUG: https://github.com/noironetworks/support/issues/916'),
        ('tempest.api.network.test_security_groups.SecGroupTest.test_create_show_delete_security_group_rule',
         'BUG: https://github.com/noironetworks/support/issues/710'),
        ('tempest.scenario.test_network_basic_ops.TestNetworkBasicOps.test_subnet_details',
         "BIG: https://github.com/noironetworks/support/issues/915"),
        ('tempest.scenario.test_network_basic_ops.TestNetworkBasicOps.test_update_router_admin_state',
         'BUG: https://github.com/noironetworks/support/issues/491'),
        ('neutron.tests.tempest.api.test_floating_ips_negative.FloatingIPNegativeTestJSON.test_associate_floatingip_with_port_with_floatingip',
         'Test uses overlapping CIDRs in the same VRF'),
        ('neutron.tests.tempest.api.test_timestamp.TestTimeStampWithSecurityGroup.test_create_sg_with_timestamp',
         'BUG: https://github.com/noironetworks/support/issues/710'),
        ('neutron.tests.tempest.api.test_timestamp.TestTimeStampWithSecurityGroup.test_create_sgrule_with_timestamp',
         'BUG: https://github.com/noironetworks/support/issues/710'),
        ('neutron.tests.tempest.api.test_timestamp.TestTimeStampWithSecurityGroup.test_show_sg_attribute_with_timestamp',
         'BUG: https://github.com/noironetworks/support/issues/710'),
        ('neutron.tests.tempest.api.test_timestamp.TestTimeStampWithSecurityGroup.test_show_sgrule_attribute_with_timestamp',
         'BUG: https://github.com/noironetworks/support/issues/710'),
        ('neutron.tests.tempest.api.test_timestamp.TestTimeStampWithSecurityGroup.test_update_sg_with_timestamp',
         'BUG: https://github.com/noironetworks/support/issues/710')
    ],
    'stable/queens': [
        ('tempest.scenario.test_network_basic_ops.TestNetworkBasicOps.test_subnet_details',
         "BIG: https://github.com/noironetworks/support/issues/915"),
        ('tempest.scenario.test_network_basic_ops.TestNetworkBasicOps.test_update_router_admin_state',
         'BUG: https://github.com/noironetworks/support/issues/491'),
        ('tempest.scenario.test_network_basic_ops.TestNetworkBasicOps.test_port_security_macspoofing_port',
         'Why is this failing?'),
        ('tempest.api.network.test_floating_ips.FloatingIPTestJSON.test_floating_ip_update_different_router',
         'Test uses overlapping CIDRs in the same VRF'),
        ('tempest.api.compute.servers.test_attach_interfaces.AttachInterfacesTestJSON.test_create_list_show_delete_interfaces_by_fixed_ip',
         'Why is this test failing?')
    ],
}

# A lot of this stuff may end up being throwaway code -- this should
# live in the pytest framework. However, I need something I can use
# until we've migrated the tests, which is why this code exists.
class Runner(object):
    """Base runner class.

    This class is used to run a family of commands for a given
    framework.
    """

    def __init__(self):
        # TODO: divine this value from config
        self.plugin_type = 'aim'
        self.undercloud_type = None
        self.KEY = None
        self.ssh_clients = {}
        localtime = datetime.datetime.now()
        env_params = {'y': datetime.datetime.now().year,
                      'm': datetime.datetime.now().month,
                      'd': datetime.datetime.now().day,
                      'h': datetime.datetime.now().hour,
                      'i': datetime.datetime.now().minute,
                      's': datetime.datetime.now().second}
        self.env_name = "%(y)s_%(m)s_%(d)s_%(h)s_%(i)s_%(s)s" % env_params

    def get_ssh_client(self, host, username='root'):
        ssh_client = self.ssh_clients.get(host)
        if not ssh_client:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.load_system_host_keys()
            print("connecting to " + host)
            ssh_client.connect(host, username=username)
            self.ssh_clients[host] = ssh_client
        return ssh_client

    def remote_cmd(self, ssh_client, cmd, wait=CMD_TIME_WAIT):
        ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(cmd)
        if wait:
            endtime = time.time() + wait
            while not ssh_stdout.channel.eof_received:
                time.sleep(1)
                if time.time() > endtime:
                    ssh_stdout.channel.close()
                    return []
        return ssh_stdout.read(), ssh_stderr.read()

    def setup_passwordless_ssh(self, user='root', hosts=None):
        for host in hosts:
            cmd ='ssh-keygen -f "/home/noiro/.ssh/known_hosts" -R %s' % host
            print(cmd)
            subprocess.check_output(['bash','-c', cmd])
            cmd1 = 'ssh -o "StrictHostKeyChecking no" %(user)s@%(host)s ' % {'user': user, 'host': host}
            cmd2 = "'ls -l'"
            cmd = cmd1 + cmd2
            print(cmd)
            subprocess.check_output(['bash','-c', cmd])
            cmd = "cat ~/.ssh/id_rsa.pub | ssh %(user)s@%(host)s 'cat >> .ssh/authorized_keys'" % {'user': user, 'host': host}
            print(cmd)
            subprocess.check_output(['bash','-c', cmd])
        subprocess.check_output(['bash','-c', cmd])

    def configure_setup_for_test(self):
        pass

    def run_test(self, test_name):
        pass

    def run_all_tests(self):
        pass

    def cleanup(self):
        pass


class TempestTestRunner(Runner):

    def __init__(self, controller = None,
                 compute1 = None, compute2 = None, ext_rtr = None,
                 undercloud_type= None):
        super(TempestTestRunner, self).__init__()
        self.controller_host = controller
        self.compute1_host = compute1
        self.compute2_host = compute2
        self.external_router = ext_rtr
        self.undercloud_type = undercloud_type
        if undercloud_type == DIRECTOR:
            self.cli_host = self.controller_host
            self.cli_user = 'heat-admin'
            self.KEY = 'source ~/' + DIRECTOR_RC + ' && '
        elif undercloud_type == JUJU:
            self.cli_host = self.external_router
            self.cli_user = 'noiro'
            self.KEY = 'source ~/' + JUJU_RC + ' && '
        else:
            print("Unsupported undercloud type: " + undercloud_type)

        self.hosts = [self.external_router, self.controller_host,
                      self.compute1_host, self.compute2_host]
        self.image_uuid = None
        self.flavor_uuid = None
        self.alt_image_uuid = None
        self.alt_flavor_uuid = None
        self.network_uuid = None
        self.version = self.get_openstack_version()

    def get_openstack_version(self):
        # we rely on the openstack client repo
        cmd1 = "cd python-openstackclient/ && "
        cmd2 = "git status | grep 'branch stable\|eol' "
        cmd3 = "| awk 'NF>1{print $NF}' && cd .."
        cmd = self.KEY + cmd1 + cmd2 + cmd3
        print(cmd)
        subprocess.check_output(['bash','-c', cmd])
        version_string = subprocess.check_output(['bash','-c', cmd]).decode('utf-8')
        version_list = [version.strip()
                        for version in version_string.split("\n") if version]
        version = version_list[0]
        if '-eol' in version:
            branch = 'stable/' + version.split('-eol')[0]
        else:
            branch = version
        return branch
        
    def configure_setup_for_test(self):
        images = [{'image': 'cirros-0.3.5-x86_64-disk.img',
                   'name': 'cirros.new'},
                  {'image': 'cirros-0.3.5-x86_64-disk.img',
                   'name': 'cirros.alt'},
                  {'image': 'ubuntu_multi_nics.qcow2',
                   'name': 'ubuntu_multi_nics'}]
        for image in images:
            image_uuid = self.upload_test_image(image_file=image['image'],
                                                image_name=image['name'])
            if image['name'] == 'cirros.new':
                self.image_uuid = image_uuid
            if image['name'] == 'cirros.alt':
                self.alt_image_uuid = image_uuid
        # for OSD and JuJu installs, we also have to configure the image flavor
        print(("undercloud type is %s" % self.undercloud_type))
        if self.undercloud_type in [DIRECTOR, JUJU]:
            print("configuring flavor UUID")
            flavor_list = [{'name': 'm1.tiny', 'cpus': '1', 'ram': '512',
                            'disk': '1', 'swap': '0'},
                           {'name': 'm1.alt_tiny', 'cpus': '1', 'ram': '512',
                            'disk': '1', 'swap': '0'},
                           {'name': 'm1.noirotest', 'cpus': '1', 'ram': '1024',
                            'disk': '8', 'swap': '0'},
                           {'name': 'm1.medium', 'cpus': '2', 'ram': '4096',
                            'disk': '40', 'swap': '0'},
                           {'name': 'm1.large', 'cpus': '4', 'ram': '8192',
                            'disk': '80', 'swap': '0'}]
            for flavor in flavor_list:
                flavor_uuid = self.configure_image_flavor(flavor)
                if flavor['name'] == 'm1.tiny':
                    self.flavor_uuid = flavor_uuid
                if flavor['name'] == 'm1.alt_tiny':
                    self.alt_flavor_uuid = flavor_uuid
        self.configure_neutron()

        self.network_uuid = self.create_external_network(self.cli_host, username=self.cli_user)
        self.create_tempest_config()
        #self.exclude_tests()

    def get_test_info(self, test):
        test_pieces = test.split(".")
        path = test_pieces[0] + "/" + "/".join(test_pieces[0:-2]) + ".py"
        test_class = test_pieces[-2:-1][0]
        test_name = test.split(".")[-1:][0]
        return path, test_class, test_name

    def exclude_tests(self):
        for test, reason in excluded_test_matrix[self.version]:
            path, test_class, test_name = self.get_test_info(test)
            def add_line(file_name, before_line, new_line):
                # find the first instance of the string
                index = None
                all_lines = None
                with open(file_name, "r") as fd:
                    all_lines = fd.readlines()
                for count in range(len(all_lines)):
                    line = all_lines[count]
                    if before_line in line:
                        strip_line = line[:-1]
                        indent_len = len(strip_line) - len(strip_line.strip())
                        indent = line[:indent_len] if indent_len else ''
                        new_line = indent + new_line
                        index = count
                        break
                if index:
                    all_lines.insert(index, new_line)
                    with open(file_name, "w+") as fd:
                        contents = "".join(all_lines)
                        fd.write(contents)
      
            cmd = "egrep testtools %s" % path
            try:
                subprocess.check_output(['bash','-c', cmd])
            except Exception as e:
                # not present, so add testtools
                add_line(path, "import", "import testtools\n")
                pass
            # need to escape backslashes
            
            reason_str = '@testtools.skip("' + reason + '")\n'
            # Skip this test
            add_line(path, 'def ' + test_name, reason_str)

    def set_ext_rtr_routes(self):
        ssh_client = self.get_ssh_client(self.external_router, username='noiro')
        cmd = ''

    def upload_test_image(self, image_file='cirros-0.3.5-x86_64-disk.img',
                          image_name='cirros.new'):
        """Upload a test image to the OpenStack controller

        This uploads a user-defined image to glance on the OpenStack
        controller. It presumes that the image is locally accessible to
        the machine running this script, that the machine has the
        OpenStack python client library installed, and that the proper
        credentials are setup in the environment (e.g. source .openrc).
        """
        cmd = self.KEY + 'openstack image show %s -c id -f value' % image_name
        try:
            image_uuid = subprocess.check_output(['bash','-c', cmd]).decode('utf-8')
            # Make sure it's a valid UUID
            try:
                image_uuid = [iuuid.strip() for iuuid in image_uuid.split("\n") if iuuid][0]
                valid_uuid = uuid.UUID(image_uuid)
                # network exists - return UUID
                print(image_uuid)
                return image_uuid
            except ValueError:
                pass
        except:
            pass

        cmd1 = "openstack image create --public"
        cmd2 = " --disk-format %s" % 'qcow2'
        cmd3 = " --container-format %s" % 'bare'
        cmd4 = " --file %s " % image_file
        cmd = self.KEY + cmd1 + cmd2 + cmd3 + cmd4 + image_name
        print(cmd)
        subprocess.check_output(['bash','-c', cmd])
        cmd = self.KEY + 'openstack image show %s -c id -f value' % image_name
        image_uuid = subprocess.check_output(['bash','-c', cmd]).decode('utf-8')
        image_uuid = [iuuid.strip() for iuuid in image_uuid.split("\n") if iuuid][0]
        print(image_uuid)
        return image_uuid

    def get_admin_project_id(self):
        cmd = self.KEY + "openstack project show admin -c id -f value"
        admin_project_uuid = subprocess.check_output(['bash','-c', cmd]).decode('utf-8')
        admin_project_uuid = [puuid.strip() for puuid in admin_project_uuid.split("\n") if puuid][0]
        print(admin_project_uuid)
        return admin_project_uuid

    def configure_image_flavor(self, flavor=None):
        """Configure image flavor for tempest tests.

        Configure a flavor used for tempest testing.
        """
        if not flavor:
            return
        print("configuring image flavor")
        cmd = self.KEY + 'openstack flavor show %s -c id -f value' % flavor['name']
        print(cmd)
        try:
            flavor_uuid = subprocess.check_output(['bash','-c', cmd]).decode('utf-8')
            # Make sure it's a valid UUID
            try:
                flavor_uuid = [iuuid.strip() for iuuid in flavor_uuid.split("\n") if iuuid][0]
                valid_uuid = uuid.UUID(flavor_uuid)
                # network exists - return UUID
                print(flavor_uuid)
                return flavor_uuid
            except ValueError:
                pass
        except:
            pass

        cmd1 = "openstack flavor create --ram %s" % flavor['ram']
        cmd2 = " --disk %s" % flavor['disk']
        cmd3 = " --vcpus %s" % flavor['cpus']
        cmd4 = " --swap %s " % flavor['swap']
        cmd5 = " --public "
        cmd = self.KEY + cmd1 + cmd2 + cmd3 + cmd4 + cmd5 + flavor['name']
        print(cmd)
        subprocess.check_output(['bash','-c', cmd])
        cmd = self.KEY + 'openstack flavor show %s -c id -f value' % flavor['name']
        flavor_uuid = subprocess.check_output(['bash','-c', cmd]).decode('utf-8')
        flavor_uuid = [iuuid.strip() for iuuid in flavor_uuid.split("\n") if iuuid][0]
        print(flavor_uuid)
        return flavor_uuid

    def configure_neutron(self):
        """Set up neutron for tempest testing.

        This configures neutron so that tempest tests can
        be run.
        """
        pass

    def create_external_network(self, host, username):
        """Create an external network for tempest testing.

        Tempest requires access to instances via a public network.
        This creates a public network that is used for tempest
        testing on noiro fabrics.
        """
        ssh_client = self.get_ssh_client(host, username=username)
        cmd = self.KEY + 'openstack network show sauto_l3out-2 -c id -f value'
        net_uuid, stderr = self.remote_cmd(ssh_client, cmd)
        if not stderr:
            net_uuid = [nuuid.strip() for nuuid in net_uuid.decode('utf-8').split("\n") if nuuid][0]
            # Make sure it's a valid UUID
            try:
                valid_uuid = uuid.UUID(net_uuid)
                # network exists - return UUID
                print(net_uuid)
                return net_uuid
            except ValueError:
                pass

        # Doesn't exist -- create it
        cmd1 = "neutron net-create sauto_l3out-2 --router:external True "
        cmd2 = "--shared --apic:distinguished_names type=dict "
        cmd3 = "ExternalNetwork=uni/tn-common/out-" + FAB_NAME + "_l3out-2/instP-" + FAB_NAME + "_l3out-2_epg"
        cmd = self.KEY + cmd1 + cmd2 + cmd3
        print(cmd)
        self.remote_cmd(ssh_client, cmd)
        cmd1 = "neutron subnet-create sauto_l3out-2 60.60.60.0/24 "
        cmd2 = "--name ext-subnet --disable-dhcp --gateway 60.60.60.1"
        cmd = self.KEY + cmd1 + cmd2
        self.remote_cmd(ssh_client, cmd)
        if self.version != 'stable/newton':
            cmd1 = "neutron subnet-create sauto_l3out-2 66.66.66.0/24 "
            cmd2 = "--name snat-subnet --gateway 66.66.66.1 --apic:snat_host_pool True"
            cmd = self.KEY + cmd1 + cmd2
            self.remote_cmd(ssh_client, cmd)
        ssh_client = self.get_ssh_client(host)
        cmd = self.KEY + 'openstack network show sauto_l3out-2 -c id -f value'
        net_uuid, _ = self.remote_cmd(ssh_client, cmd)
        net_uuid = net_uuid.decode('utf-8')
        print(net_uuid)
        print(_)
        net_uuid = [nuuid.strip() for nuuid in net_uuid.split("\n") if nuuid][0]
        print(net_uuid)
        return net_uuid

    def queens_auth(self, auth_cfg):
        split_cfg = auth_cfg.split('\n')
        split_cfg.remove('tempest_roles = member')
        split_cfg.remove('admin_domain_name = %(admin_domain_name)s')
        split_cfg.remove('use_dynamic_credentials = true')
        return '\n'.join(split_cfg)

    def queens_identity(self, identity_cfg):
        split_cfg = identity_cfg.split('\n')
        for idx, cfg in enumerate(split_cfg):
            if '= v3' in cfg:
                split_cfg[idx] = cfg.replace('v3', 'v2')
        return '\n'.join(split_cfg)

    def queens_identity_feature(self, identity_feature_cfg):
        split_cfg = identity_feature_cfg.split('\n')
        for idx, cfg in enumerate(split_cfg):
            if 'api_v3' in cfg:
                split_cfg[idx] = cfg.replace('v3', 'v2')
        return '\n'.join(split_cfg)

    def create_tempest_config(self):
        ssh_client = self.get_ssh_client(self.external_router, username='noiro')
        cmd = 'tempest init %s' % self.env_name
        print(cmd)
        self.remote_cmd(ssh_client, cmd)
        # Get the IP address of the OpenStack controller
        cmd = self.KEY + "echo $OS_AUTH_URL | awk -F'/' '{print $3}' | awk -F':' '{print $1}'"
        controller_ip, _ = self.remote_cmd(ssh_client, cmd)
        controller_ip = [ip.strip() for ip in controller_ip.decode('utf-8').split("\n") if ip][0]
        if self.undercloud_type == 'juju':
            admin_domain_name = 'admin_domain'
            admin_role = 'Admin'
        else:
            admin_domain_name = 'Default'
            admin_role = 'admin'
        tempest_params = {}
        # Need to fix auth for queens.
        if self.version == 'stable/queens':
            for idx, cfg in enumerate(cfg_template.ALL_TEMPLATES):
                if '[auth]' in cfg:
                    cfg_template.ALL_TEMPLATES[idx] = self.queens_auth(cfg)
                elif '[identity-feature-enabled]' in cfg:
                    cfg_template.ALL_TEMPLATES[idx] = self.queens_identity(cfg)
                elif '[identity]' in cfg:
                    cfg_template.ALL_TEMPLATES[idx] = self.queens_identity_feature(cfg)
        tempest_params.update({'cwd': os.getcwd() + '/' + self.env_name,
                               'image_uuid': self.image_uuid,
                               'flavor_uuid': self.flavor_uuid,
                               'alt_image_uuid': self.alt_image_uuid,
                               'alt_flavor_uuid': self.alt_flavor_uuid,
                               'controller_ip': controller_ip,
                               'controller_password': 'noir0123',
                               'admin_project_id': self.get_admin_project_id(),
                               'external_network': self.network_uuid,
                               'admin_domain_name': admin_domain_name,
                               'admin_role': admin_role})
        tempest_cfg = [cfg % tempest_params for cfg in cfg_template.ALL_TEMPLATES]
        tempest_conf_file = '%s/etc/tempest.conf' % self.env_name
        cfg_file = open(tempest_conf_file,'w') 
        for cfg in tempest_cfg:
            cfg_file.write(cfg)
        cfg_file.close()
        testr_dot_conf_file = '%s/.testr.conf' % self.env_name
        dot_conf_file = open(testr_dot_conf_file,'w') 
        for cfg in TESTR_DOT_CONF:
            dot_conf_file.write(cfg)
        dot_conf_file.close()

    def run_test(self, test_name):
        cmd = 'ostestr --regex %s' % test_name
        subprocess.check_output(['bash','-c', cmd])

    def run_all_tests(self, host):
        # Create a tempest environment, using the local date/time
        ssh_client = self.get_ssh_client(host)
        cmd = 'cd %s && tempest run' % self.env_name
        self.remote_cmd(ssh_client, cmd, wait=TEMPEST_WAIT_TIME)
        #subprocess.check_output(['bash','-c', cmd])

    def cleanup(self):
        ssh_client = self.get_ssh_client(self.controller_host)
        cleanup_tempest(self.plugin_type, ssh_client)


class NoiroTestRunner(Runner):

    def __init__(self, ext_rtr=None):
        super(NoiroTestRunner, self).__init__()
        self.external_router = ext_rtr
        self.ssh_client = self.get_ssh_client(ext_rtr, username='noiro')

    def configure_setup_for_test(self):
        # Run the noirotest setup
        cmd = 'cd noirotest && python setup.py'
        self.remote_cmd(self.ssh_client, cmd, wait=NOIRO_SETUP_WAIT_TIME)

    def save_results(self, test, out, err):
        results_filename = '%(env)s_%(test)s_results' % {'env': self.env_name,
                                                         'test': test}
        results_file = open(results_filename, 'w') 
        results_file.write(out)
        results_file.write(err)
        results_file.close()

    def run_noirotest_ml2_sanity(self):
        cmd = PPATH + 'cd noirotest/testcases/testcases_sanity && python run_ml2_sanity.py'
        out, err = self.remote_cmd(self.ssh_client, cmd, wait=ML2_SANITY_WAIT_TIME)
        self.save_results('ml2_sanity', out, err)

    def run_noirotest_gbp_sanity(self):
        cmd = PPATH + 'cd noirotest/testcases/testcases_sanity && python run_gbp_sanity.py'
        out, err = self.remote_cmd(self.ssh_client, cmd, wait=GBP_SANITY_WAIT_TIME)
        self.save_results('gbp_sanity', out, err)

    def run_noirotest_east_west_datapath(self):
        cmd = PPATH + 'cd noirotest/testcases/testcases_dp && python test_dp_runner.py'
        out, err = self.remote_cmd(self.ssh_client, cmd, wait=EAST_WEST_WAIT_TIME)
        self.save_results('east_west', out, err)

    def run_noirotest_north_south_datapath(self):
        cmd = PPATH + 'cd noirotest/testcases/testcases_nat_func && python test_gbp_nat_suite.py'
        out, err = self.remote_cmd(self.ssh_client, cmd, wait=NORTH_SOUTH_WAIT_TIME)
        self.save_results('north_south', out, err)

    def run_noirotest(self):
        self.run_noirotest_ml2_sanity()
        self.run_noirotest_gbp_sanity()
        self.run_noirotest_east_west_datapath()
        self.run_noirotest_north_south_datapath()

    def cleanup(self, host):
        pass


class NautoPostDeployRunner(Runner):
    """Class to fix issues with Nauto deployments.

    The nauto deployer has been deprecated in favor of OpenStack
    Director (OSD) deploys. As a result, certain bugs have crept in to
    the nauto deployer since it is no longer supported. However,
    until the OSD deployer is ready, we will still use nauto for this,
    and therefore need to fix the issues from a given deploy.
    """

    def __init__(self, controller = None,
                 compute1 = None, compute2 = None, ext_rtr = None):
        self.controller_host = controller
        self.compute1_host = compute1
        self.compute2_host = compute2
        self.external_router = ext_rtr
        self.hosts = [self.external_router, self.controller_host,
                      self.compute1_host, self.compute2_host]
        self.image_uuid = None
        self.network_uuid = None
        super(NautoPostDeployRunner, self).__init__()

    def cleanup_dead_agents(self):
        ssh_client = self.get_ssh_client(self.controller_host)
        cmd = self.KEY + "for agent in `neutron agent-list | grep xxx | awk -F'|' '{print $2}'`; do neutron agent-delete $agent; done"
        print(cmd)
        self.remote_cmd(ssh_client, cmd)

    def get_dhcp_hosts(self):
        """Return compute hosts running DHCP agent.
    
           Return all compute hosts running the DHCP agent.
        """
        ssh_client = self.get_ssh_client(self.controller_host)
        cmd = self.KEY + "neutron agent-list | grep dhcp | awk -F'|' '{print $4}'"
        print(cmd)
        hosts, _ = self.remote_cmd(ssh_client, cmd)
        hosts = hosts.decode('utf-8')
        return [host.strip() for host in hosts.split("\n") if host]

    def update_dhcp_agent_cfg(self, ssh_client):
        """Fix the neutron-dhcp-agent configuration..
    
           Our nauto installer has a bug where it fails to configure
           the DHCP agent to use force_metadata (needed because there is
           no reference implementation neutron router in the network).
           This sets the force_metadata option to True and restarts
           the neutron-dhcp-agent service.
        """
        SED_FIND = '#force_metadata = false'
        SED_REPLACE = 'force_metadata = true'
        FILE = '/etc/neutron/dhcp_agent.ini'
        cmd = "sed -i 's/" + SED_FIND + "/" + SED_REPLACE + "/g' " +  FILE
        print(cmd)
        self.remote_cmd(ssh_client, cmd)
        cmd = "service neutron-dhcp-agent restart"
        print(cmd)
        self.remote_cmd(ssh_client, cmd)

    def restart_metadata_agent(self, ssh_client):
        """Restart metdata agent.
    
           Our nauto installer has a bug where it fails to configure
           the metadata agent correctly on all compute hosts except
           the first. This function kills supervisord on the host,
           deletes all the flows on br-fabric, and restarts the neutron-opflex-agent,
           which will use create new metadata agents using the updated
           configuration file.
        """
        cmd = "kill `ps -ef | grep [s]upervisord | awk -F' ' '{print $2}'`"
        print(cmd)
        self.remote_cmd(ssh_client, cmd)
        cmd = "ovs-ofctl del-flows br-fabric"
        print(cmd)
        self.remote_cmd(ssh_client, cmd)
        cmd = "service neutron-opflex-agent restart"
        print(cmd)
        self.remote_cmd(ssh_client, cmd)

    def fix_br_fabric(self, ssh_client):
        cmd1 = "ovs-vsctl --may-exist add-port br-fabric br-fab_vxlan0 -- "
        cmd2 = "set Interface br-fab_vxlan0 type=vxlan options:remote_ip=flow "
        cmd3 = "options:key=flow options:dst_port=8472"
        cmd = cmd1 + cmd2 + cmd3
        print(cmd)
        self.remote_cmd(ssh_client, cmd)

    def restart_agent_ovs(self, ssh_client):
        cmd = "service agent-ovs restart"
        print(cmd)
        self.remote_cmd(ssh_client, cmd)

    def clear_iptables_rule(self, ssh_client):
        cmd = CLEAR_IP_TABLES_RULE
        print(cmd)
        self.remote_cmd(ssh_client, cmd)

    def update_agent_ovs_cfg(self, ssh_client):
        """Fix the agent-ovs configuration..
    
           Our nauto installer has a bug where it configures
           the SSL option as "enabled" in agent-ovs, which is
           an invalid value. This function replaces enabled
           with the correct value of "encrypted"
        """
        SED_FIND = '"mode": "enabled"'
        SED_REPLACE = '"mode": "encrypted"'
        FILE = '/etc/opflex-agent-ovs/conf.d/opflex-agent-ovs.conf'
        cmd = "sed -i 's/" + SED_FIND + "/" + SED_REPLACE + "/g' " +  FILE
        print(cmd)
        self.remote_cmd(ssh_client, cmd)

    def get_compute_hosts(self):
        """Return all the compute hosts in the deployment. """
        ssh_client = self.get_ssh_client(self.controller_host)
        cmd = self.KEY + "nova service-list  | grep nova-compute | awk -F'|' '{print $4}'"
        print(cmd)
        hosts, _ = self.remote_cmd(ssh_client, cmd)
        hosts = hosts.decode('utf-8')
        return [host.strip() for host in hosts.split("\n") if host]

    def update_metadata_agent_cfg(self, hosts):
        """Fix the neutron-metaata-agent configuration.
    
           Our nauto installer has a bug where it fails to configure
           the metadata agent correctly on all compute hosts except
           the first. This scp's the configuration file from the first
           compute host to all the others
        """
        ssh_client = self.get_ssh_client(self.controller_host)
        # get the file from the first compute host
        PATH = '/etc/neutron/'
        FILE = 'metadata_agent.ini'
        cmd = ('scp root@%(host)s:%(path)s%(file)s .' %
               {'host': hosts[0], 'file': FILE, 'path': PATH})
        print(cmd)
        self.remote_cmd(ssh_client, cmd)
        # now copy it back down to the other compute hosts
        for host in hosts[1:]:
            cmd = ("scp %(file)s root@%(host)s:%(path)s%(file)s" %
                   {'host': host, 'file': FILE, 'path': PATH})
            print(cmd)
            self.remote_cmd(ssh_client, cmd)

    def apply_fixes(self):
        self.setup_passwordless_ssh(user='noiro', hosts=[self.external_router])
        self.setup_passwordless_ssh(hosts=[self.controller_host,
                                           self.compute1_host,
                                           self.compute2_host])
        self.cleanup_dead_agents()
        dhcp_host = self.get_dhcp_hosts()[0]
        print("DHCP host is " + dhcp_host)
        all_hosts = self.get_compute_hosts()
        self.update_metadata_agent_cfg(all_hosts)
        for host in all_hosts:
            ssh_client = self.get_ssh_client(host)
            if host == dhcp_host:
                self.update_dhcp_agent_cfg(ssh_client)
            self.update_agent_ovs_cfg(ssh_client)
            if host != all_hosts[0]:
                self.restart_metadata_agent(ssh_client)
            self.fix_br_fabric(ssh_client)
            self.restart_agent_ovs(ssh_client)
            self.clear_iptables_rule(ssh_client)

@click.command()
@click.option('--controller-ip',
              help='IP address of OpenStack controller')
@click.option('--router-ip',
              help='IP address of External Router VM')
@click.option('--undercloud-type',
              help='Type of undercloud (juju or director)')
def make_tempest_config(controller_ip, router_ip, undercloud_type):
    if not controller_ip:
        try:
            fd = open('./controller_ip.txt', 'r')
            controller_ip = fd.readline().strip()
        except IOError as e:
            print(("Couldn't open %s" % './controller_ip.txt'))
            sys.exit(0)
    if not router_ip:
        try:
            fd = open('./router_ip.txt', 'r')
            router_ip = fd.readline().strip()
        except IOError as e:
            print(("Couldn't open %s" % './router_ip.txt'))
            sys.exit(0)
    if not undercloud_type:
        try:
            fd = open('./undercloud_type.txt', 'r')
            undercloud_type = fd.readline().strip()
        except IOError as e:
            print(("Couldn't open %s" % './undercloud_type.txt'))
            sys.exit(0)
    runner = TempestTestRunner(controller=controller_ip, ext_rtr=router_ip, undercloud_type=undercloud_type)
    runner.configure_setup_for_test()
    click.echo("Iniitialization complete, and tempest config generated")

if __name__ == '__main__':
    make_tempest_config()
