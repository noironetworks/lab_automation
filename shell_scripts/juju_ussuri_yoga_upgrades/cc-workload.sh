#!/bin/bash

while true; do
    status=$(juju status | grep -E 'maintenance|executing')
    if [[ -n $status ]]; then
	    echo "Found 'maintenance' or 'executing' in the status. Sleeping..."
	    sleep 10  # Adjust the sleep duration as needed
    else
	    break;
    fi
done

