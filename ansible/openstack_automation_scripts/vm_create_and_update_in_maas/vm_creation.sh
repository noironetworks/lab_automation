name=$1
cpu=$2
memory=$3
disk_size=$4
bridge=$5

if [ ! -f "vm_sessions.yaml" ]; then
    echo "vms:" > vm_sessions.yaml
fi

sudo virt-install \
--hvm \
--connect qemu:///system \
--network=bridge:$bridge,model=virtio \
--pxe \
--name $name \
--boot network \
--memory=$memory \
--vcpus=$cpu \
--os-type=linux \
--graphics spice \
--disk path=/var/lib/libvirt/images/$name.img,size=$disk_size

uu_id=$(virsh dumpxml $name | grep -oP '(?<=<uuid>).*(?=<\/uuid>)')
vm_mac_address=$(virsh dumpxml $name | grep -oP "(?<=<mac address=').*?(?='/>)")

# Write filenames to output.txt
cat <<EOF >> vm_sessions.yaml
  - name: $name
    uuid: $uu_id
    mac_address: $vm_mac_address
EOF
