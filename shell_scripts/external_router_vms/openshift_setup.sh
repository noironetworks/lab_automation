#!/bin/bash

# Print help text and exit.
if [ "$#" -ne 3 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
  echo "Usage: openshift_setup.sh <openstack_project_name> <openshift_cluster_name> <openshift_domain_name>"
  echo
  echo "Examples:"
  echo "   openshift_setup.sh new_project openshift4 noiro.local"
  exit 1
fi

PRJ_NAME=$1
echo "openstack_project_name: ${PRJ_NAME}"
CLUSTER_NAME=$2
echo "openshift_cluster_name: ${CLUSTER_NAME}"
DOMAIN_NAME=$3
echo "openshift_domain_name: ${DOMAIN_NAME}"

source /home/noiro/overcloudrc

# TBD: There is some version mismatch issue so this quota set command
#      won't work on the external router VM. You will have to run this
#      command on the fab undercloud for now then.
openstack quota set --class --cores 72 --ram 114688 default

openstack project create ${PRJ_NAME}
openstack role add --user admin --project ${PRJ_NAME} _member_
openstack role add --user admin --project ${PRJ_NAME} swiftoperator
openstack object store account set --property Temp-URL-Key=superkey

PRJ_ID="$(openstack project show -f value -c id ${PRJ_NAME})"
echo "project ID: ${PRJ_ID}"
GUI_URL="$(more /home/noiro/overcloudrc | grep no_proxy | cut -d ',' -f 2)"
echo "Horizon URL: ${GUI_URL}"

# Generate the clouds.yaml file
cat <<EOF > clouds.yaml
clouds:
  openstack:
    auth:
      auth_url: http://${GUI_URL}:5000/v3
      username: "admin"
      password: "noir0123"
      project_id: ${PRJ_ID}
      project_name: "${PRJ_NAME}"
      user_domain_name: "Default"
    region_name: "regionOne"
    interface: "public"
    identity_api_version: 3
EOF

FIP_SUBNET_ID="$(openstack subnet list | grep "60.60.60" | cut -d ' ' -f 2)"
echo "FIP subnet ID: ${FIP_SUBNET_ID}"
neutron floatingip-create --tenant-id ${PRJ_ID} --floating-ip-address 60.60.60.199 --subnet ${FIP_SUBNET_ID} sauto_l3out-2

openstack flavor create --public --ram 16384 --disk 80 --vcpus 8 aci_rhel_huge

PUB_SSH_KEY="$(cat ~/.ssh/id_rsa.pub)"
echo "noiro public SSH key: ${PUB_SSH_KEY}"

# Generate the install-config.yaml file
cat <<EOF > install-config.yaml
apiVersion: v1
baseDomain: ${DOMAIN_NAME}
compute:
- hyperthreading: Enabled
  name: worker
  platform: {}
  replicas: 1
controlPlane:
  hyperthreading: Enabled
  name: master
  platform: {}
  replicas: 1
metadata:
  creationTimestamp: null
  name: ${CLUSTER_NAME}
networking:
  clusterNetwork:
  - cidr: 10.128.0.0/14
    hostPrefix: 23
  machineCIDR: 10.0.0.0/16
  networkType: OpenShiftSDN
  serviceNetwork:
  - 172.30.0.0/16
platform:
  openstack:
    cloud: openstack
    computeFlavor: aci_rhel_huge
    externalDNS: ["172.23.136.143", "172.23.136.144"]
    externalNetwork: sauto_l3out-2
    lbFloatingIP: 60.60.60.199
    octaviaSupport: "0"
    region: ""
    trunkSupport: "1"
proxy:
  httpsProxy: "http://proxy.esl.cisco.com:80/"
  httpProxy: "http://proxy.esl.cisco.com:80/"
  noProxy: "localhost,127.0.0.1,172.16.0.99,172.16.0.100,172.16.0.101,172.16.0.102,172.16.0.103,172.16.0.104,10.0.0.10,10.0.0.11,10.0.0.12,10.0.0.13,10.0.0.14,10.0.0.15,10.0.0.16,10.0.0.17,10.0.0.18,10.0.0.19,10.0.0.20,172.28.184.150,oauth-openshift.apps.${CLUSTER_NAME}.${DOMAIN_NAME},console-openshift-console.apps.${CLUSTER_NAME}.${DOMAIN_NAME},downloads-openshift-console.apps.${CLUSTER_NAME}.${DOMAIN_NAME},${GUI_URL}"
publish: External
pullSecret: '{"auths":{"cloud.openshift.com":{"auth":"b3BlbnNoaWZ0LXJlbGVhc2UtZGV2K2lyYXRob3JlMXg3aXluY3Y0b2x0c3Z1Z2l1N29wZmR5a3FwOlJETjY1QjVORElQQ1BEUkJPNUlLMkdGV01KNE83MTM2VVMyNERJQjY0MkRWR09NSTU3MTRGSE9PSzFMNFpJVkc=","email":"irathore@cisco.com"},"quay.io":{"auth":"b3BlbnNoaWZ0LXJlbGVhc2UtZGV2K2lyYXRob3JlMXg3aXluY3Y0b2x0c3Z1Z2l1N29wZmR5a3FwOlJETjY1QjVORElQQ1BEUkJPNUlLMkdGV01KNE83MTM2VVMyNERJQjY0MkRWR09NSTU3MTRGSE9PSzFMNFpJVkc=","email":"irathore@cisco.com"},"registry.connect.redhat.com":{"auth":"NTMxNDE1ODR8dWhjLTFYN2l5TkN2NE9MVHN2dWdpdTdvUGZEeWtxUDpleUpoYkdjaU9pSlNVelV4TWlKOS5leUp6ZFdJaU9pSmlOak5rTldSalpqazRZVFUwWlRnME9ESTVOVGN3TkRWbVltSTBaVFEzTUNKOS5sTHBJYXFwTXA1d19qaEFRbGp3WXR0T2tNNjNtMlBNRFM4N21VNTJPMVVTUnBKM1RCbG51QnJ4blhMQWhxVlYyQ19wNVFpRzlDWk52UWFQWlktNko4Z0NEdnhiWmVMa0gyRlh0MTZud0ZXSkRFU0VEQ1VBQWJIR2ZLcjNlU3JCeUZac3VQMDlDdnNJZ2tyU1lfdmQ3MGpCa045M0pmV2I1eWdtaFBIaHpaT2ZnVGowbnB2V3NmNjlCbk5nZlZSdEZtUnlUclFTWVlLM2pCX0NZUEVtSEpRam44MGhRWlJyQkppeU9kT1hhN1R3UHdza29jT1BGOENuclZtRnowaUltSFhTWmVnMEFwOUhPNTZraVVlRDBkVmxhNWtudUlyYk83N01nSVVMd2s3TVNWdlJTd3RIMnJfVy1XWGtoQkduWFoxRDREQXh2LXZfWVE0NVlhRFVzYkRIZGVrZnIybjhfRk4yckJ4UkZNUVNXMGROYlpKaHpadFBxc2dMLVdQM2V1eDJWM2twWHQxcG14Sk5RQTAyUlNMV194bnhEZEVRRFlPWHNhZlRnQjZySE5rWTYzRFA0UzNHWXNlbnlta3Y1VG5YanZWaTZpb2V1TVU2RHpEVjNsYTV6RkxZbWY0cXhiUTJSQkwzY254eEtaY3hmcXlhNFE2NWQwUUVoWEZ1dHRCeGJUM0NvLUR0RGhCZXRLVDJTNm5FZUpRVmlxeWxGVVRxSkJsS2xyaEg4eVhXY3haWFFpeU1kSVBXdjJHWFdITncwTTdlZ1dEQjJrSFUxdmg2enBPV2Q1VkRMcGtybWpCU2JfdkJVcDNWdFBNMHBKMW90VmZXQ1ZOYlpBSHpEVzRkRUc5c2t1dEJvck8wQVEtcjIxdjBTanlYVHppWnZiTDBHdTUxSnRaTQ==","email":"irathore@cisco.com"},"registry.redhat.io":{"auth":"NTMxNDE1ODR8dWhjLTFYN2l5TkN2NE9MVHN2dWdpdTdvUGZEeWtxUDpleUpoYkdjaU9pSlNVelV4TWlKOS5leUp6ZFdJaU9pSmlOak5rTldSalpqazRZVFUwWlRnME9ESTVOVGN3TkRWbVltSTBaVFEzTUNKOS5sTHBJYXFwTXA1d19qaEFRbGp3WXR0T2tNNjNtMlBNRFM4N21VNTJPMVVTUnBKM1RCbG51QnJ4blhMQWhxVlYyQ19wNVFpRzlDWk52UWFQWlktNko4Z0NEdnhiWmVMa0gyRlh0MTZud0ZXSkRFU0VEQ1VBQWJIR2ZLcjNlU3JCeUZac3VQMDlDdnNJZ2tyU1lfdmQ3MGpCa045M0pmV2I1eWdtaFBIaHpaT2ZnVGowbnB2V3NmNjlCbk5nZlZSdEZtUnlUclFTWVlLM2pCX0NZUEVtSEpRam44MGhRWlJyQkppeU9kT1hhN1R3UHdza29jT1BGOENuclZtRnowaUltSFhTWmVnMEFwOUhPNTZraVVlRDBkVmxhNWtudUlyYk83N01nSVVMd2s3TVNWdlJTd3RIMnJfVy1XWGtoQkduWFoxRDREQXh2LXZfWVE0NVlhRFVzYkRIZGVrZnIybjhfRk4yckJ4UkZNUVNXMGROYlpKaHpadFBxc2dMLVdQM2V1eDJWM2twWHQxcG14Sk5RQTAyUlNMV194bnhEZEVRRFlPWHNhZlRnQjZySE5rWTYzRFA0UzNHWXNlbnlta3Y1VG5YanZWaTZpb2V1TVU2RHpEVjNsYTV6RkxZbWY0cXhiUTJSQkwzY254eEtaY3hmcXlhNFE2NWQwUUVoWEZ1dHRCeGJUM0NvLUR0RGhCZXRLVDJTNm5FZUpRVmlxeWxGVVRxSkJsS2xyaEg4eVhXY3haWFFpeU1kSVBXdjJHWFdITncwTTdlZ1dEQjJrSFUxdmg2enBPV2Q1VkRMcGtybWpCU2JfdkJVcDNWdFBNMHBKMW90VmZXQ1ZOYlpBSHpEVzRkRUc5c2t1dEJvck8wQVEtcjIxdjBTanlYVHppWnZiTDBHdTUxSnRaTQ==","email":"irathore@cisco.com"}}}'
sshKey: |
  ${PUB_SSH_KEY}
EOF

# Disable the lines below if this script has been run once after the re-deployment
eval "$(ssh-agent -s)"
ssh-add /home/noiro/.ssh/id_rsa

