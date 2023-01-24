#!/usr/bin/python

import logging as log
import paramiko
import time

#from apicapi import apic_client

CMD_TIME_WAIT = 15
plugin_type = 'aim'

KEY='source ~/keystonerc_admin && '
apic_ip='172.28.184.40'
apic_username='admin'
apic_password='noir0123'
ssl='True'

host = '172.28.184.45'
default_username = 'root'
default_password = 'noir0123'


def remote_cmd(ssh_client, cmd, wait=True):
    ssh_stdin, ssh_stdout, ssh_stderr = ssh_client.exec_command(cmd)
    error_output = ssh_stderr.read()
    if error_output:
        # TODO: Not sure what to do here -- some stderr is
        #       warnings (e.g. deprecated commands)
        print(error_output)
    if wait:
        endtime = time.time() + CMD_TIME_WAIT
        while not ssh_stdout.channel.eof_received:
            time.sleep(1)
            if time.time() > endtime:
                ssh_stdout.channel.close()
                return []
    return ssh_stdout.read()

#channel = ssh.get_transport().open_session()
#channel.execute_command("some command here")
# Wait for it to finish
#while not channel.exit_status_ready():
#    time.sleep(1)

#def cleanup_legacy_tenants():
#    apic_session = apic_client.RestClient(log, "", [apic_ip],
#                                          apic_username, apic_password, ssl)
#    apic_session.login()
#    classes = ['fvTenant']
#    [apic_session.delete_class(x) for x in classes]


def cleanup_aim_tenants(ssh_client):
    # Clean up all the AIM tenants. We need to exclude APIC-specific
    # tenants such as common and infra, so we grep for tenants that
    # begin with prj_ prefixes (OpenStack ACI plugin convention). We
    # also exclude tenants that are still configured in openstack.
    cmd = KEY + " openstack project list -c ID  -f value"
    print(cmd)
    os_tids_raw = remote_cmd(ssh_client, cmd)
    exclude_tids = [exclude_tid.strip() for exclude_tid in os_tids_raw.split("\n") if exclude_tid]
    cmd = "aimctl manager tenant-find -p | grep prj_"
    print(cmd)
    aim_tids_raw = remote_cmd(ssh_client, cmd)
    del_tids = [aim_tid.strip() for aim_tid in aim_tids_raw.split("\n")
                if aim_tid and aim_tid not in exclude_tids]

    
    for del_tid in del_tids:
        cmd = "aimctl manager tenant-delete %s --force --cascade" % del_tid
        print(cmd)
        remote_cmd(ssh_client, cmd)


def cleanup_floating_ips(ssh_client):
    cmd = KEY + "neutron floatingip-list -F id -f value"
    print(cmd)
    fiplist_raw = remote_cmd(ssh_client, cmd)
    fiplist = [fip.strip() for fip in fiplist_raw.split("\n") if fip]
    for fip in fiplist:
        cmd = KEY + "neutron floatingip-delete %s" % fip
        print(cmd)
        remote_cmd(ssh_client, cmd)

def cleanup_buggy_networks(ssh_client):
    # TODO(tbachman): We need to understand why there's a neutron network
    #                 resource without any AIM/AID constructs left over
    #                 after a tempest run. For now, just clean it up
    cmd = KEY + "neutron net-list -F id -F name -f value | grep tempest | awk -F' ' '{print $1}'"
    print(cmd)
    netlist_raw = remote_cmd(ssh_client, cmd)
    netlist = [net.strip() for net in netlist_raw.split("\n") if net]
    for net in netlist:
        cmd = 'echo "' + "delete from networks where id='" + net +"';" + '"' + " >> /tmp/delete-tempest.txt"
        remote_cmd(ssh_client, cmd)
    if netlist:
        cmd = "mysql neutron < /tmp/delete-tempest.txt"
        print(cmd)
        remote_cmd(ssh_client, cmd)
        cmd = "rm -f /tmp/delete-tempest.txt"
        print(cmd)
        remote_cmd(ssh_client, cmd)

def cleanup_tempest(plugin_type, ssh_client):
    cleanup_floating_ips(ssh_client)
    if plugin_type == 'aim':
        cleanup_buggy_networks(ssh_client)
        cleanup_aim_tenants(ssh_client)
    #else:
    #    cleanup_legacy_tenants(ssh_client)
    cmd = KEY + "neutron subnet-delete ext-subnet"
    print(cmd)
    remote_cmd(ssh_client, cmd)
    cmd = KEY + "neutron net-delete Datacenter-Out"
    print(cmd)
    remote_cmd(ssh_client, cmd)
