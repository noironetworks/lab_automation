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

#from cleanup_tempest import cleanup_tempest
#import tempest_conf as cfg_template

JUJU='juju'
DIRECTOR='director'
JUJU_RC='admin-openrc.sh'
DIRECTOR_RC='overcloudrc'
PPATH='export PYTHONPATH=/home/noiro/noirotest && '
CMD_TIME_WAIT = 15
with open('~/junk/fab_name.txt') as f:
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

    def configure_setup_for_test(self):
        pass

    def cleanup(self):
        pass


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
        results_filename = '%(env)s_%(test)s_results' % {'env': self.env_name, 'test': test}
        with open(results_filename, 'w') as results_file:
            results_file.write(out.decode('utf-8'))
            results_file.write(err.decode('utf-8'))

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

@click.command()
@click.option('--controller-ip',
              help='IP address of OpenStack controller')
@click.option('--router-ip',
              help='IP address of External Router VM')
@click.option('--undercloud-type',
              help='Type of undercloud (juju or director)')
def helper(controller_ip, router_ip, undercloud_type):
    if not controller_ip:
        try:
            fd = open('~/junk/controller_ip.txt', 'r')
            controller_ip = fd.readline().strip()
        except IOError as e:
            print(("Couldn't open %s" % './controller_ip.txt'))
            sys.exit(0)
    if not router_ip:
        try:
            fd = open('~/junk/router_ip.txt', 'r')
            router_ip = fd.readline().strip()
        except IOError as e:
            print(("Couldn't open %s" % './router_ip.txt'))
            sys.exit(0)
    if not undercloud_type:
        try:
            fd = open('~/junk/undercloud_type.txt', 'r')
            undercloud_type = fd.readline().strip()
        except IOError as e:
            print(("Couldn't open %s" % '~/junk/undercloud_type.txt'))
            sys.exit(0)
    runner = NoiroTestRunner(ext_rtr=router_ip)
    runner.configure_setup_for_test()
    #runner.run_noirotest()

if __name__ == '__main__':
    helper()
