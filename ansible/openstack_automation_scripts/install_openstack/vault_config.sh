#!/bin/bash
# Set the VAULT_ADDR
vault_address=$(juju status | awk '/vault\/[0-9]+/ {print $5}')
export VAULT_ADDR="http://$vault_address:8200"

# Check if VAULT_ADDR is set
if [ -z "$VAULT_ADDR" ]; then
	echo "Error: VAULT_ADDR is not set. Exiting."
	 return 1
fi

# Initialize Vault
vault operator init -key-shares=5 -key-threshold=3 > vault_init.txt 

# Extract unseal keys and initial root token from the output
unseal_keys=$(grep "Unseal Key" vault_init.txt | awk '{print $NF}')
initial_root_token=$(grep "Initial Root Token" vault_init.txt | awk '{print $NF}')

# Unseal Vault using the first three unseal keys
for ((i = 1; i <= 3; i++)); do
	key=$(echo "$unseal_keys" | sed -n "${i}p")
        echo "Unsealing with key: $key"
	vault operator unseal "$key"
done

sleep 20
# Set the initial root token
export VAULT_TOKEN="$initial_root_token"
echo "$VAULT_TOKEN"

# Check if VAULT_TOKEN is set
if [ -z "$VAULT_TOKEN" ]; then
	echo "Error: VAULT_TOKEN is not set. Exiting."	 
	 return 1
fi

# Create a new token with a TTL of 10 minutes
new_token=$(vault token create -ttl=10m -format=json | jq -r '.auth.client_token')

# Authorize the new token with the Vault leader charm
echo "Authorize with token: $new_token"
juju run-action --wait vault/leader authorize-charm token="$new_token"

