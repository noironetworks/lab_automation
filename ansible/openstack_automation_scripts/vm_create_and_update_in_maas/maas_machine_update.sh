host_name=$1
uuid=$2
vm_mac_address=$3
hypervisor_user=$4
maas_user=$5
hypervisor_password=$6
hypervisor_ip=$7


system_id=$(maas admin machines read mac_address=$vm_mac_address | grep system_id |tail -n 1 )

system_idd=$(echo "$system_id" | awk -F'"' '{print $4}')
echo "$system_idd"

#maas admin machine update $system_idd   power_type=virsh   power_parameters='{"power_address": "qemu+ssh://root@172.28.184.224/system", "power_user": "admin", "power_pass": "noir0123", "power_id": '"$uuid"'}'
maas admin machine update $system_idd \
  hostname=$host_name \
  power_type=virsh \
  power_parameters="{\"power_address\": \"qemu+ssh://$hypervisor_user@$hypervisor_ip/system\", \"power_user\": \"$maas_user\", \"power_pass\": \"$hypervisor_password\", \"power_id\": \"$uuid\"}"

 maas admin machine commission $system_idd enable_ssh=1
 