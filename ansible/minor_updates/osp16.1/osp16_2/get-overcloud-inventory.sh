#!/usr/bin/bash

help="${0##*/}: [-h] <file>

Write a basic inventory in <file>.

This script must be run from the undercloud.
The script assumes that the control plane is named ctlplane.
"

while getopts :h OPT; do
    case $OPT in
        h)
            echo "${help}"
            exit 0
            ;;
        *)
            echo "${help}"
            exit 2
    esac
done
shift $(( OPTIND - 1 ))
OPTIND=1

inv_file="${1:?Please provide the destination inventory file name, see -h for more.\n}"

. stackrc

openstack server list --format json | \
    jq -r '.[]|.Name +"|"+ .Networks' | \
    awk -F'|' '
/ctlplane=/{hosts[$1]=gensub("ctlplane=","","",$2)}
END{
  print("undercloud ansible_connection=local")
  print("[overcloud:vars]\nansible_user=heat-admin\n[overcloud]");
  for (host in hosts){
    print(host " ansible_host=" hosts[host])
  }
}' > "${inv_file}"

