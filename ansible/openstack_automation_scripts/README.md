# Openstack Installation User Guide


## Table of Contents
- [Overview](#overview)
- [Hardware and software requirements](#hardware-and-software-requirements)
- [Installation and Configuration](#installation-and-configuration)
   * [Hypervisor Configuration](#hypervisor-configuration)
   * [Create and Configure MaaS VM](#create-and-configure-maas-vm)
   * [Create Juju, Controller, Compute VMs etc](#create-juju-controller-compute-vms-etc)
   * [Install Openstack](#install-openstack)
   * [Openstack Post Install](#openstack-post-install)
   * [Uninstall MaaS, Juju (if required)](#uninstall-maas-juju-if-required)
- [Troubleshooting](#troubleshooting)
- [References](#references)


## Overview
This document provides instructions to install Openstack Using MaaS and Juju. Most of the installation commands are automated using shell / ansible scripts. The installation is mainly divided into three sections
- Creating MaaS VM and MaaS, Juju configuration on it.
- Creating Openstack cluster VMs and adding them on MaaS GUI.
- Installation of Openstack


## Hardware and software requirements
- A virtualisation enabled physical machine with Ubuntu(20.04/22.04) OS, this machine will act as hypervisor.

- Openstack cluster nodes (compute, controller/network, dashboard etc) are going to be Virtual Machines. Even the MaaS machine is a VM. Recommended memory, cpus and disk are as below

   | Virtual Machine | Memory(Mb)| vCPU  | Disk(Gb) |
   | :-------------: | :-------: | :---: | :------: |
   |  MaaS           |   8192    |   4   |   100    |
   |  Juju           |   4096    |   2   |   50     |
   |  Controller     |   16384   |   4   |   100    |
   |  Dashboard      |   4096    |   1   |   20     |
   |  Compute        |   8192    |   4   |   100    |


## Installation and Configuration

### Hypervisor Configuration
1. Install required virtualization packages

   ```sh
   sudo apt install qemu-kvm libvirt
   sudo apt install virt-install virt-manager
   ```

2. Create PXE bridge on hypervisor machine, the bridge will be used by MaaS, Juju, Controller, Compute VMs during vm creation.

   ```sh
   TODO: add commands
   ```

### Create and Configure MaaS VM
1. Create MaaS VM using virt-manager. Install Ubuntu 22.04 on this MaaS VM.

   (Check [References](#references) section for how to do it)

2. SSH into MaaS VM and

    - set http_proxy, https_proxy and no_proxy env variables. Please adjust no_proxy as per your setup.

        ```sh
        export http_proxy="http://proxy.esl.cisco.com:80"
        export https_proxy="http://proxy.esl.cisco.com:80"
        export no_proxy="127.0.0.1,localhost,10.30.120.0/24,1.11.1.0/24,172.28.184.8,2.28.184.18"
        ```

    - install ansible pkg

        ```sh
        sudo apt update
        sudo apt install ansible
        ```

3. Install MaaS, Juju and configure MaaS VM.

   - SSH into MaaS VM. Clone repo in $HOME directory

       `git clone https://github.com/noironetworks/lab_automation $HOME`

   - Copy only required installation folder to $HOME

       `cp -r $HOME/lab_automation/ansible/openstack_automation_scripts $HOME`.

   - Go to directory `cd $HOME/openstack_automation_scripts/maas_and_juju_install_and_configure` and follow below given instructions on MaaS VM to configure MaaS service using ansible scripts

       - Update `config.yaml` with appropriate details.
       - Run `ansible-playbook install_maas_juju.yaml`. This will install maas, juju services and create maas admin user.
       - Run `ansible-playbook configure_maas.yaml`. This will do maas service initial configuration e.g setting NTP, DNS, HTTP_PROXY, downloading ubuntu images for vm commissioning, updating PXE bridge subnet with IP Range, subnet Gateway IP, enabling dhcp on the subnet etc

            OR

        - You can [follow link](https://maas.io/tutorials/build-a-maas-and-lxd-environment-in-30-minutes-with-multipass-on-ubuntu#6-log-into-maas) to configure MaaS via GUI. Set NTP Server, DNS forwarder, APT & HTTP/HTTPS proxy server, download Ubuntu 22.04, 20.04 images, upload ssh key etc.


       - Run `ansible-playbook configure_juju.yaml`. This will do initial juju configuration like add-cloud, add credentials etc


### Create Juju, Controller, Compute VMs etc
1. SSH back into the hypervisor machine. Clone same git repo in $HOME directory

   `git clone https://github.com/noironetworks/lab_automation $HOME`

2. Copy only required installation folder to $HOME

    `cp -r $HOME/lab_automation/ansible/openstack_automation_scripts $HOME`.

3. Go to directory

   `cd $HOME/openstack_automation_scripts/vm_create_and_update_in_maas`

4. Create Openstack cluster VMs

   - Run following scripts on hypervisor machine to create PXE boot enabled openstack cluster VMs using virt-install command. Before running the script, update pxe bridge name, vm details etc. in `config.yaml` and then

       Run `ansible-playbook -e "@config.yaml" vm_creation.yaml`

       OR

   - Create openstack cluster VMs using virt-manager as you created MaaS VM

5. Once VMs are created and running, MaaS will detect those VMs automatically. We need to update each VM power settings so that MaaS can orchestrate VM lifecycle.

   - A file `vm_sessions.yaml` is created on the hypervisor machine in folder `$HOME/openstack_automation_scripts/vm_create_and_update_in_maas` as part of "Create Openstack cluster VMs" step. This file contains VM details like name, mac address, uuid. Mac address is used to identify the corresponding vm/machine in MaaS. Copy this file from hypervisor machine to MaaS VM in `$HOME/openstack_automation_scripts/vm_create_and_update_in_maas/` directory and then

       Run `ansible-playbook -e "@vm_sessions.yaml" -e "@config.yaml" maas_machine_update.yaml`

       OR

   - You can update VM Power Settings using MaaS GUI and Start VM "Commission". [Reference Link](https://ubuntu.com/blog/quick-add-kvms-for-maas?_ga=2.178578468.1006774203.1713332492-1331330862.1713332492)


### Install Openstack

This section will instruct how to install Openstack `Antelope` on the cluster VMs. Follow steps:

- SSH back into MaaS VM and Go to installation scripts directory

    `cd $HOME/openstack_automation_scripts/install_openstack`.

- Update `vars.yaml` with
    -  `openstack_version` name you want to install from allowed list:
        `["antelope", "bionic-queens", "bionic-rocky", "bionic-stein", "bionic-train", "bionic-ussuri","focal-ussuri", "focal-wallaby", "focal-xena", "focal-yoga", "focal-zed"]`

    -   correct VM names as detected / configured in MaaS. (These VM names should be same as what you used in file `$HOME/openstack_automation_scripts/vm_create_and_update_in_maas/config.yaml` to create VMs)

- Update external interface name in `antelope/antelope_opflex_sfc.yaml`
   `bridge-interface-mappings: br-ex: <iface-name>`

    **Note**: A seaparate folder is present under `install_openstack` for every openstack version and that folder has its respective `*-opflex-sfc.yaml` file. Update this file as per your setup environment

- Run `ansible-playbook -i vars.yaml install_openstack.yaml`. This will take around 2 hours depending on your network speed.

- After successfull installation you can see `openrc` file created in `$HOME` directory


### Openstack Post Install
After openstack installation is successful Run `ansible-playbook -i vars.yaml openstack_post_installation.yaml`. This will
- use openstackclient CLI to upload images, create network, subnet, security group rules, vms.
- test traffic between vms using ping/ssh


### Uninstall MaaS, Juju (if required)
Go to directory `cd $HOME/openstack_automation_scripts/maas_and_juju_install_and_configure` and run `ansible uninstall_maas_and_juju.yaml` (and reboot the MaaS VM if possible).

Note: Issues are seen while re-installing maas on the same VM e.g Subnets are not detected automatically by MaaS and you don't see subnets in the MaaS GUI. So its recommended to create new MaaS VM and do MaaS installation on the new VM.


## Troubleshooting

1. On a MaaS vm check following config files are properly configured or not

    ```sh
    /etc/maas/regiond.conf:
        database_host: localhost
        database_name: maasdb
        database_pass: 3aEdyxMbi8RW
        database_port: 5432
        database_user: maas
        maas_url: http://10.30.120.118:5240/MAAS

    /etc/maas/rackd.conf:
        cluster_uuid: 3191655e-f633-4a15-bd39-484cf91c195e
        maas_url:
        - http://localhost:5240/MAAS
    ```

2. To address the issue of subnets not being detected in MAAS, which can occur due to multiple reinstallation attempts or stale resources, you can manually add the subnets, reconfigure MAAS components (such as maas-region, maas-rack, maas-dhcp), and perform a reinstallation of MAAS. Follow these steps to resolve the issue effectively:

    1. Manually Add Subnets in MAAS
        - Access the MAAS Web Interface: Log in to the MAAS web interface using your browser.
        - Navigate to Subnets: Go to the "Subnets" section in the MAAS interface.
        - Add Fabric: click on Add fabric option and add fabric without entering any name.
        - Add Subnet: Click on "Add Subnet" and provide the necessary details for the subnet that is not detected automatically. Ensure that the subnet configuration matches your network setup.

    2. Reconfigure MAAS Components
        After manually adding the subnets, reconfigure the MAAS components to ensure proper network discovery and management.
        - Reconfigure maas-region-controller:

            `sudo dpkg-reconfigure maas-rack-controller`

          Follow the prompts to reconfigure the MAAS region controller component.

        - Reconfigure maas-rack-controller:

            `sudo dpkg-reconfigure maas-rack-controller`

           Follow the prompts to reconfigure the MAAS rack controller component.

        - Reconfigure maas-dhcp:

            `sudo dpkg-reconfigure maas-dhcp`

    3. Reinstall MAAS



## References
- [Create VM using virt-manager](https://medium.com/@DrewViles/using-libvirt-kvm-qemu-to-create-vms-792e49262304)
- [Openstack Antelope Installation Guide](https://docs.openstack.org/project-deploy-guide/charm-deployment-guide/2023.1/index.html)
- [Quick-add KVMs for MAAS](https://ubuntu.com/blog/quick-add-kvms-for-maas?_ga=2.178578468.1006774203.1713332492-1331330862.1713332492)
