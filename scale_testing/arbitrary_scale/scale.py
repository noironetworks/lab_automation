import argparse
import errno
import subprocess
import os


from pcf_terraform import pcf_terraform_template
from tenant_terraform import tenant_terraform_template


ROUTER = 'router'
DIRECTOR = 'director'

DIRECTOR_RC = 'overcloudrc'


class TestProject(object):
    """Class to manage reesources for a test project

    This class is used to instantiate test projects, based
    on a set of parameters:
    * Number of networks per project
    * Number of VMs per project

    It can of course be modified to have different types and
    dimensions of scaling per project.
    """
    def __init__(self, cloud_ip, tenant_count, tenant_prefix, simulated_ports):
        self.cloud_ip = cloud_ip
        self.tenant_count = int(tenant_count)
        self.tenant_prefix = tenant_prefix
        self.simulated_ports = simulated_ports
        self.created_dirs = []
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

    def create_address_scope(self):
        """Create address scope in common tenant

        Create a VRF in the common tenant, which can
        be used for inter-tenant communication without
        using an L3 Out policy. We have to do this using
        subprocess because terraform doesn't support using
        resource extensions (e.g. to pass our DNs).
        """
        cmd = 'openstack address scope list'
        data = self.local_command(cmd)
        cmd = 'openstack address scope create --apic-distinguished-names VRF=uni/tn-common/ctx-%(vrf)s --shared --ip-version 4 interconnect_vrf'
        self.local_coammand(cmd)

    def local_command(self, command):
        cmd = self.KEY + command
        print(cmd)
        result_string = subprocess.check_output(['bash','-c', cmd]).decode('utf-8')
        result_list = [result.strip()
                       for result in result_string.split("\n") if result]
        return result_list

    def create_resources(self):
        for count in range(self.tenant_count):
            tenant = self.tenant_prefix + str(count)
            self.create_tenant_terraform(tenant)

    def create_pcf_terraform(self):
        pass

    def create_ds_terraform(self):
        pass

    def create_tenant_terraform(self, tenant):
        # Create the directory structure for the new project
        project_dir = os.getcwd() + '/' +  tenant
        try:
            print("Making directory %s" % project_dir)
            os.mkdir(project_dir)
        except OSError as e:
            if e.errno == errno.EEXIST:
                print('Directory not created.')
            else:
                raise
        self.created_dirs.append(project_dir)
        terraform_dict = {'ip': self.cloud_ip, 'project': tenant}
        with open(project_dir + '/' + 'main.tf', 'w+' ) as fd:
            fd.write(tenant_terraform_template % terraform_dict)

    def get_ports(self, tenant, port_filter=None):
        cmd = 'openstack port list '
        cmd += '--project %s ' % tenant
        cmd += '--device-owner compute:nova -c ID -f value -c "MAC Address" -f value'
        if port_filter:
            cmd += ' ' + port_filter
        port_info = []
        try:
            port_info = self.local_command(cmd)
        except subprocess.CalledProcessError as e:
            print("Error from command: %s" % e)
        print(port_info)

    def cleanup_terraform(self):
        pass

    def create_port_scripts(self):
        pass


def run():
    parser = argparse.ArgumentParser(description='Scale test manager')
    parser.add_argument('--cloud-ip',default="10.30.120.201",
                         help='IP Address of OpenStack horizon.')
    parser.add_argument('--tenant-count',default=1,
                         help='Number of tenants to create resources in.')
    parser.add_argument('--tenant-prefix',default='prj',
                         help='Tenant name prefix')
    parser.add_argument('--simulated-ports',default=False, action='store_true',
                         help='Create simulated VMs (i.e. bound ports only).')

    args = parser.parse_args()
    tester = TestProject(args.cloud_ip, args.tenant_count, args.tenant_prefix, args.simulated_ports)
    tester.create_resources()

if __name__ == '__main__':
    run()
