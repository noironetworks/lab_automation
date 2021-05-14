############################################################################
# 4.2. New memory requirements
############################################################################
# 1. Create bash script to verfiy system meets minimum memory requirements
cat > mem_requirement_check.sh << EOL
#!/bin/sh
MEM_MINIMUM=25165824
CURRENT_MEM=\$(cat /proc/meminfo  | grep MemTotal | awk '{print \$2}')
if [ "\${CURRENT_MEM}" -lt "\${MEM_MINIMUM}" ]; then
    echo "\${CURRENT_MEM} is less than minimum memory requirement of \${MEM_MINIMUM}"
    exit
fi
EOL
# 2. Make the bash script executable
chmod +x mem_requirement_check.sh
# 3. Run the memory check script
./mem_requirement_check.sh
