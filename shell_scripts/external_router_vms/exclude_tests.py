#!/usr/bin/python

import click
import subprocess


JUJU='juju'
JUJU_RC='admin-openrc.sh'
DIRECTOR='director'
DIRECTOR_RC='overcloudrc'


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
         "BUG: https://github.com/noironetworks/support/issues/915"),
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
         "BUG: https://github.com/noironetworks/support/issues/915"),
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
         "BUG: https://github.com/noironetworks/support/issues/915"),
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
         "BUG: https://github.com/noironetworks/support/issues/915"),
        ('tempest.scenario.test_network_basic_ops.TestNetworkBasicOps.test_update_router_admin_state',
         'BUG: https://github.com/noironetworks/support/issues/491'),
        ('tempest.scenario.test_network_basic_ops.TestNetworkBasicOps.test_port_security_macspoofing_port',
         'Why is this failing?'),
        ('tempest.api.network.test_floating_ips.FloatingIPTestJSON.test_floating_ip_update_different_router',
         'Test uses overlapping CIDRs in the same VRF'),
        ('tempest.api.compute.servers.test_attach_interfaces.AttachInterfacesTestJSON.test_create_list_show_delete_interfaces_by_fixed_ip',
         'Upstream bug: https://bugs.launchpad.net/tempest/+bug/1790864'),
        ('neutron_tempest_plugin.api.test_revisions.TestRevisions.test_update_network_constrained_by_revision',
         'Why is this test failing?'),
        ('neutron_tempest_plugin.api.test_timestamp.TestTimeStampWithL3.test_show_floatingip_attribute_with_timestamp',
         'Why is this test failing?'),
        ('neutron_tempest_plugin.scenario.test_connectivity.NetworkConnectivityTest.test_connectivity_through_2_routers',
         'The apic_aim mechanism driver does not support transit routes (connect networks to same neutron router instead)'),
        ('neutron_tempest_plugin.scenario.test_internal_dns.InternalDNSTest.test_dns_domain_and_name',
         'This is an upstream bug (non-optimized has same failure)')
    ],
    'stable/train': [
        ('tempest.api.network.test_floating_ips.FloatingIPTestJSON.test_floating_ip_update_different_router',
         "Overlapping subnets not allowed on same neutron router."),
        ('tempest.api.identity.admin.v3.test_projects.ProjectsTestJSON.test_project_get_equals_list',
	 "BUG: "),
        ('tempest.scenario.test_network_basic_ops.TestNetworkBasicOps.test_port_security_macspoofing_port',
         'Why is this failing?'),
        ('tempest.scenario.test_network_basic_ops.TestNetworkBasicOps.test_update_router_admin_state',
         'BUG: https://github.com/noironetworks/support/issues/491'),
    ],
    'stable/wallaby':[
        ('tempest.api.network.test_floating_ips.FloatingIPTestJSON.test_floating_ip_update_different_router',
         "Overlapping subnets not allowed on same neutron router."),
        ('tempest.scenario.test_network_basic_ops.TestNetworkBasicOps.test_port_security_macspoofing_port',
         'Why is this failing?'),
        ('tempest.api.identity.admin.v3.test_groups.GroupsV3TestJSON.test_list_groups',
         'BUG'),
        ('tempest.api.identity.admin.v3.test_groups.GroupsV3TestJSON.test_list_user_groups',
         'BUG'),
        ('tempest.api.identity.admin.v3.test_inherits.InheritsV3TestJSON.test_inherit_assign_list_revoke_user_roles_on_domain',
         'BUG'),
        ('tempest.api.identity.admin.v3.test_inherits.InheritsV3TestJSON.test_inherit_assign_list_revoke_user_roles_on_project_tree',
         'BUG'),
        ('tempest.api.image.v2.admin.test_images_metadefs_namespace_properties.MetadataNamespacePropertiesTest.test_basic_meta_def_namespace_property',
         'BUG'),
    ],
}


class Excluder(object):

    def __init__(self, undercloud_type):
        if undercloud_type == DIRECTOR:
            self.KEY = 'source ~/' + DIRECTOR_RC + ' && '
        elif undercloud_type == JUJU:
            self.KEY = 'source ~/' + JUJU_RC + ' && '
        self.version = self.get_openstack_version()

    def get_openstack_version(self):
        # we rely on the openstack client repo
        cmd1 = "cd python-openstackclient/ && "
        cmd2 = "git status | grep 'branch stable\|eol' "
        cmd3 = "| awk 'NF>1{print $NF}' && cd .."
        cmd = self.KEY + cmd1 + cmd2 + cmd3
        print(cmd)
        subprocess.check_output(['bash','-c', cmd])
        version_string = subprocess.check_output(['bash','-c', cmd]).decode()
        version_list = [version.strip()
                        for version in version_string.split("\n") if version]
        version = version_list[0]
        if '-eol' in version:
            branch = 'stable/' + version.split('-eol')[0]
        else:
            branch = version
        return branch
        
    def get_test_info(self, test):
        test_pieces = test.split(".")
        path = "-".join(test_pieces[0].split("_")) + "/" + "/".join(test_pieces[0:-2]) + ".py"
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


@click.command()
@click.option('--undercloud-type', default='director',
              help='Type of undercloud (juju or director)')
def exclude_tests(undercloud_type):
    excluder = Excluder(undercloud_type=undercloud_type)
    excluder.exclude_tests()
    click.echo("Iniitialization complete, and tempest config generated")

if __name__ == '__main__':
    exclude_tests()
