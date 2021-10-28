#!/bin/bash
while read -r line
do
  deployment_name=$(echo $line | cut -d"|" -f2)
  deployment_id=$(echo $line | cut -d"|" -f3)
  parent_name=$(echo $line | cut -d"|" -f7)
  echo "deployment=$deployment_name ($deployment_id) parent $parent_name"
  openstack software deployment output show $deployment_id --all --long
  echo "---"
done < <(openstack stack resource list --nested-depth 5 overcloud | grep "OS::Heat::\(Software\|Structured\)Deployment " | grep "FAILED")
