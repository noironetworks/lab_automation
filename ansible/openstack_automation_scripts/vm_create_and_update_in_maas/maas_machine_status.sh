vm_mac_address=$1
system_id=$(maas admin machines read mac_address=$vm_mac_address | grep system_id |tail -n 1 )

system_idd=$(echo "$system_id" | awk -F'"' '{print $4}')
while true; do
    # Get the status of the machine
    STATUS=$(maas admin machine read $system_idd | grep -o '"status_name": "[^"]*"' | cut -d'"' -f4)

    # Check if the status is "Ready"
    if [ "$STATUS" = "Ready" ]; then
        echo "Machine is ready!"
        break
    else
        echo "Status is $STATUS. Waiting for the machine to become ready..."
        sleep 30  # Adjust the sleep time as needed
    fi
done


maas admin machine power-off $system_idd
