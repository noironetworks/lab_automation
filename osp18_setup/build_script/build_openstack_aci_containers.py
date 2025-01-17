#!/usr/libexec/platform-python

import configparser
import datetime
import getpass
import glob
import grp
import argparse
import os
import pwd
import shutil
import shlex
import sys
import subprocess
import tarfile
import tempfile
import json
import re
import pdb
from hashlib import md5

CISCOACI_RPMDIR = "/opt/cisco_aci_rpms"


def file_repo_path(repotext):
    lines = repotext.split("\n")
    for line in lines:
        if "baseurl" in line:
            if line.split("=")[1].split(":")[0] == 'file':
                return line.split("=")[1].split(":")[1][2:]

def pull_containers(upstream_registry, regseparator,
                     pushurl, pushtag, container_name, arr, repotext,
                     license_text, release_tag):
    print("Pulling ACI %s container" % container_name)
    if "aci_container" in arr.keys():
        print("here")
        aci_container = "%s/%s" %(pushurl, arr['aci_container'])
        src_container = "registry.connect.redhat.com/noiro/%s" %(arr['aci_container'])
    else:
        aci_container = "%s/%s-ciscoaci" % (pushurl, arr['rhel_container'])
        src_container = "registry.connect.redhat.com/noiro/%s-ciscoaci" % (arr['rhel_container'])


    pcmd ="podman pull %s:%s" % (src_container, release_tag)
    print(pcmd)
    subprocess.check_call(shlex.split(pcmd))
    tcmd  =  "podman tag  %s:%s %s:%s" % (src_container, release_tag, aci_container, release_tag)
    print(tcmd)
    subprocess.check_call(shlex.split(tcmd))
    cmd ="podman push --local %s/%s:%s  %s/osp18/%s" % ("localhost", aci_container,release_tag, pushurl, aci_container)
    print(cmd)
    subprocess.check_call(shlex.split(cmd))

def build_containers(upstream_registry, regseparator,
                     pushurl, pushtag, container_name, arr, repotext,
                     license_text, release_tag, additional_repos, repo_tar_file,
                     rhel_version):
    print("Building ACI %s container" % container_name)

    aci_pkgs = arr['packages']
    docker_run_cmds = arr['run_cmds']

    if "opflex" in container_name:
	    rhel_container = "%s%s%s:%s" % ("localhost", regseparator,
		  		    arr['rhel_container'], "latest")
    else:
	    rhel_container = "%s%s%s:%s" % (upstream_registry, regseparator,
                                    arr['rhel_container'], release_tag)


    if "aci_container" in arr.keys():
        aci_container = "%s" %(arr['aci_container'])
    else:
        aci_container = "%s-ciscoaci" % ( arr['rhel_container'])
    
    if 'user' in arr.keys():
        user = arr['user']
    else:
        user = ''

    if 'summary' in arr.keys():
        summary = arr['summary']
    else:
        summary = ''

    if 'description' in arr.keys():
        description = arr['description']
    else:
        description = ''


    d_user = subprocess.check_output(
        ['podman', 'run', '--net=host', '--name', '%s-temp' % container_name, rhel_container, 'whoami'])
    def_user = d_user.decode('utf-8').strip()

    subprocess.check_call(["podman", "rm", '%s-temp' % container_name])

    build_dir = tempfile.mkdtemp()
    # We only need to copy the repo data over if we're using the tarball
    source_path = '/opt/cisco_aci_repo' if repo_tar_file else file_repo_path(repotext)
    if source_path:
        shutil.copytree(source_path, '%s/opt/cisco_aci_repo' % build_dir)
    repofile = os.path.join(build_dir, 'aci.repo')
    with open(repofile, 'w') as fh:
       fh.write(repotext)
    license_file = os.path.join(build_dir, 'LICENSE.txt')
    with open(license_file, 'w') as fh:
       fh.write(license_text)

    blob = """
FROM %s
MAINTAINER Cisco Systems
LABEL name="%s" vendor="Cisco Systems" version="%s" release="1" summary="%s" \
description="%s"
USER root
ENV no_proxy="${no_proxy}"
       """ % (rhel_container, aci_container, release_tag, summary, description)
    blob = blob + "RUN dnf --releasever=%s config-manager --enable openstack-17.1-for-rhel-9-x86_64-rpms %s\n" % (rhel_version,  additional_repos)
    if source_path:
        blob = blob + "ADD %s %s \n" % (source_path, source_path)
    blob = blob + "Copy aci.repo /etc/yum.repos.d \n"
    if "opflex" not in container_name:
	    blob = blob + "RUN mkdir /licenses \n"
    blob = blob + "Copy LICENSE.txt /licenses/ \n"
    for cmd in docker_run_cmds:
        blob = blob + "RUN %s \n" % cmd
    blob = blob + "RUN dnf --releasever=%s -y update-minimal --security --sec-severity=Important --sec-severity=Critical && dnf clean all \n" % rhel_version
    if user == '':
        blob = blob + "USER \"\" \n"
    else:
        blob = blob + "USER %s \n" % user

    dockerfile = os.path.join(build_dir, "Dockerfile")
    with open(dockerfile, 'w') as df:
        df.write(blob)

    subprocess.check_call(["podman", "build", build_dir, "-t",
                           "%s:%s" % (aci_container, pushtag)])

    #subprocess.check_call(["podman", "build", build_dir, "-t",
    #                       "%s" % (aci_container)])

    cmd ="podman push %s/%s  %s/osp18/%s" % ("localhost", aci_container, pushurl, aci_container)
    subprocess.check_call(shlex.split(cmd))

    shutil.rmtree(build_dir)

    #subprocess.check_call(["podman", "rmi", rhel_container])

    #ccmd ="podman rmi %s:%s" % (aci_container, pushtag)
    #subprocess.check_call(shlex.split(ccmd))


def main():
    timestamp = datetime.datetime.now().strftime('%s')

    def extant_file(x):
        if not os.path.exists(x):
           raise argparse.ArgumentTypeError("{0} does not exist".format(x))
        return x

    parser = argparse.ArgumentParser(description='Build containers for ACI Plugin')

    parser.add_argument("-o", "--output_file",
                      help="Environment file to create, default is /home/stack/templates/ciscoaci_containers.yaml",
                      dest='output_file', default='/home/stack/templates/ciscoaci_containers.yaml')
    parser.add_argument("-c", "--container",
                      help="Containers to build, comma separated, default is all", dest='containers_tb', default='all')
    parser.add_argument("-s", "--upstream",
                      help="Upstream registry to pull base images from, eg. registry.access.redhat.com/rhosp13, defaults to registry.access.redhat.com/rhosp13",
                      default='registry.redhat.io/rhoso',
                      dest='upstream_registry')
    parser.add_argument("-d", "--destregistry",
                      help="Destination registry to push to, eg: 1.100.1.1:8787/rhosp13",
                      dest='destination_registry')
    parser.add_argument("-r", "--regseparator",
                      help="Upstream registry separator for images, eg. '/' for normal upstream registrys (default). Will be added between upstream registry name and container name. Use '_' for satellite based registries.",
                      default="/",
                      dest='regseparator')
    parser.add_argument("-i", "--image-tag", help="Upstream release tag for images, defaults to 18.03",
                      default='18.03', dest='release_tag')
    parser.add_argument("-t", "--tag", help="tag for images, defaults to current timestamp",
                      default=timestamp, dest='tag')
    parser.add_argument("-a", "--additional-repos",
                      help="Additional repos to use when building containers (defaults to empty list). Use with 'rhel-8-for-x86_64-baseos-eus-rpms rhel-8-for-x86_64-appstream-eus-rpms' when using satellite.",
                      nargs='*',
                      default=[],
                      dest='additional_repos')
    parser.add_argument("--force", help="Override check for md5sum mismatch",
	              dest='force', action='store_true')
    parser.add_argument("-p", "--pull",
                      help="Pull upstream containers instead of building locally",
                      dest='pull',
                      action='store_true')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--aci_repo_file",
                      dest='aci_repo_file',
		      type=extant_file,
		      metavar="FILE",
                      help="Path to yum repoistory file, which describes the repository which provides ACI plugin rpm files.\n If you want this script to create a repository on undercloud, please use the -z option to provide path to openstack-aci-rpms-repo tar file downloaded from cisco website")
    group.add_argument("-z", "--aci_rpm_repo_tar_file",
                      dest='repo_tar_file',
		      type=extant_file,
		      metavar="FILE",
                      help="Path to openstack-aci-rpms-repo tar file. This will be use to create a local yum repository on undercloud")

    options = parser.parse_args()


    current_user = getpass.getuser()
    current_grp = grp.getgrgid(pwd.getpwnam(current_user).pw_gid).gr_name

    rhel_version = "9.4"
    print("rhel version = {}".format(rhel_version))

    if options.repo_tar_file:
       m=md5()
       with open(options.repo_tar_file, 'rb') as fh:
         data = fh.read()
       m.update(data)
       md5sum = m.hexdigest()

       with open('/opt/ciscoaci-tripleo-heat-templates/tools/dist_md5sum') as fh:
           expected_md5sum = fh.read()

       if not (md5sum == expected_md5sum.strip()):
          if not options.force:
             print("md5sum of provided tar file does not match with expected. Use --force to disable this check'")
             sys.exit(1)

       os.system("sudo rm -rf /opt/cisco_aci_repo")
       os.system("sudo /usr/bin/mkdir -p /opt/cisco_aci_repo")
       os.system("sudo chown {0} /opt/cisco_aci_repo".format(current_user))
       os.system("sudo chgrp {0} /opt/cisco_aci_repo".format(current_grp))
       tf = tarfile.open(options.repo_tar_file)
       tf.extractall('/opt/cisco_aci_repo')
       repotext = """
[acirepo]
name=aci repo
baseurl=file:///opt/cisco_aci_repo
enabled=1
gpgcheck=0
       """ 

    pushurl = None
    if options.destination_registry:
        pushurl = options.destination_registry
    """
    else:
        cmd = "openstack tripleo container image list -f json"
        print("Running cmd '%s' to get local registry" % cmd)
        output = subprocess.check_output(shlex.split(cmd))
        jl = json.loads(output)
        for el in jl:
           if re.search('ironic', el['Image Name']):
              rg = re.search('^docker://([^/]*)' , el['Image Name'])
              if rg:
                 pushurl = "%s/ciscoaci" % rg.groups()[0]
              else:
                 print("Unable to determine local registry")
                 sys.exit(1)
              break
    if pushurl == None:
        print("Unable to determine local registry")
        sys.exit(1)

	"""

    container_array = {
        'neutron-server': {
            "user": "neutron",
            "rhel_container": "openstack-neutron-server-rhel9",
            "packages": [],
            "run_cmds": ["yum --releasever={} -y install python3-apicapi python3-neutron-opflex-agent libmodelgbp python3-openstack-neutron-gbp python3-gbpclient python3-aci-integration-module ".format(rhel_version)],
            "osd_param_name": ["ContainerNeutronApiImage", "ContainerNeutronConfigImage"],
            "summary":"This is Ciscoaci modified Neutron API container",
            "description":"This will be deployed on the controller  nodes",
        },
        'ciscoaci-lldp': {
            "rhel_container": "openstack-neutron-server-rhel9",
            "aci_container": "openstack-ciscoaci-lldp",
            "packages": [],
            "run_cmds": ["yum --releasever={} -y install python3-aci-integration-module python3-neutron-opflex-agent ethtool python3-apicapi lldpd ".format(rhel_version)],
            "osd_param_name": ["ContainerCiscoLldpImage"],
            "summary":"This is Ciscoaci LLDP container",
            "description":"This will be deployed on the controller and compute nodes",
        },
        'horizon': {
            "rhel_container": "openstack-horizon-rhel9",
            "packages": [],
            "run_cmds": ["yum --releasever={} -y install python3-openstack-dashboard-gbp".format(rhel_version),
                         "mkdir -p /usr/lib/heat"],
            "osd_param_name": ["ContainerHorizonImage"],
            "summary":"This is Ciscoaci modified Horizon container",
            "description":"This will be deployed on the controller  nodes",

        },
        'heat': {
            "user": "heat",
            "rhel_container": "openstack-heat-engine-rhel9",
            "packages": [],
            "run_cmds": ["yum --releasever={} -y install python3-openstack-heat-gbp python3-gbpclient".format(rhel_version),
                         "mkdir -p /usr/lib/heat",
                         "cp -r /usr/lib/python3.9/site-packages/gbpautomation /usr/lib/heat"],
            "osd_param_name": ["ContainerHeatEngineImage"],
            "summary":"This is Ciscoaci modified HeatEngine container",
            "description":"This will be deployed on the controller  nodes",
        },
        'ciscoaci-aim': {
            "user": "neutron",
            "rhel_container": "openstack-neutron-server-rhel9",
            "aci_container": "openstack-ciscoaci-aim",
            "packages": [],
            "run_cmds": ["yum --releasever={} -y install python3-apicapi python3-aci-integration-module python3-neutron-opflex-agent python3-openstack-neutron-gbp python3-gbpclient ".format(rhel_version),
                         "update-crypto-policies --set LEGACY", "chown -R neutron:neutron /run/aid"],
            "osd_param_name": ["ContainerCiscoAciAimImage", "ContainerCiscoAciAimConfigImage"],
            "summary":"This is Ciscoaci AIM container",
            "description":"This will be deployed on the controller nodes",
        },
	'neutron-openvswitch-agent': {
            "user": "neutron",
            "rhel_container": "openstack-neutron-base-rhel9",
	    "aci_container": "openstack-ciscoaci-neutron-openvswitch-agent",
            "packages": [],
            "run_cmds": ["dnf -y install openstack-neutron-openvswitch --allowerasing && dnf clean all && rm -rf /var/cache/dnf"],
            "osd_param_name": ["ContainerCiscoAciNeutronOpenvswitchAgentImage"],
            "summary":"This is Ciscoaci Neutron openvswitch agent container",
            "description":"This will be deployed on the controller nodes",	
	    },
        'opflex-agent': {
            "user": "neutron",
            "rhel_container": "openstack-ciscoaci-neutron-openvswitch-agent",
            "aci_container": "openstack-ciscoaci-opflex",
            "packages": [],
            "run_cmds": ["yum --releasever={} -y install opflex-agent opflex-agent-renderer-openvswitch noiro-openvswitch-lib noiro-openvswitch-otherlib ethtool python3-neutron-opflex-agent python3-apicapi python3-openstack-neutron-gbp lldpd os-net-config".format(rhel_version)],
            "osd_param_name": ["ContainerOpflexAgentImage"],
            "summary":"This is Ciscoaci Opflex Agent container",
            "description":"This will be deployed on the controller and compute nodes",
        },
        'neutron-opflex-agent': {
            "user": "neutron",
            "rhel_container": "openstack-ciscoaci-neutron-openvswitch-agent",
            "aci_container": "openstack-ciscoaci-neutron-opflex",
            "packages": [],
            "run_cmds": ["yum --releasever={} -y install ethtool python3-neutron-opflex-agent python3-apicapi python3-openstack-neutron-gbp".format(rhel_version)],
            "osd_param_name": ["ContainerNeutronOpflexAgentImage"],
            "summary":"This is Ciscoaci Neutron Opflex Agent container",
            "description":"This will be deployed on the controller and compute nodes",
        },
    }

    license_text = """
         Copyright 2020 Cisco Systems, Inc.
  
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

""" 
    if options.containers_tb == 'all':
        containers_list = container_array.keys()
    else:
        containers_list = []
        for co in options.containers_tb.split(','):
            if co in container_array.keys():
                containers_list.append(co)
            else:
                print("Unknown container name %s, skipping" % co)

    additional_repos = ''
    for repo in options.additional_repos:
        additional_repos += "--enable %s " % repo
    if not options.pull:
        print("Will rebuild containers localy")
        for container in containers_list:
            build_containers(options.upstream_registry, options.regseparator, pushurl,
                  options.tag, container, container_array[container], repotext, license_text,
                  options.release_tag, additional_repos, options.repo_tar_file, rhel_version)
        mytag = options.tag
    else:
        print("Will pull containers from upstream repo")
        for container in containers_list:
           pull_containers(options.upstream_registry, options.regseparator, pushurl,
                  options.tag, container, container_array[container], repotext, license_text,
                  options.release_tag) 
        mytag = options.release_tag

    config_blob = "parameter_defaults:\n"
    for container in containers_list:
       param_names = container_array[container]['osd_param_name']
       if "aci_container" in container_array[container].keys():
          container_name = container_array[container]['aci_container']
       else:
          container_name = "%s-ciscoaci" % container_array[container]['rhel_container']
       print("container = {}".format(container_name))
       for pn in param_names:
          config_blob = config_blob + \
                "   %s: %s:%s \n" % (
                    pn, container_name, mytag)
    with open(options.output_file, "w") as fh:
       fh.write(config_blob)


if __name__ == "__main__":
    main()

