This directory and its subdirectories contain code to support testing of
various scale scenarios for OpenStack clouds. The intended test scenarios
are:
* Reproduce simulated scale of a customers setup
* Create arbitrary scale on an OpenStack cloud
* OpenShift on OpenStack scale

A subdirectory exists for each intended workflow.

There are several types of configuration that must be pushed:
1) OpenStack configuration
2) OpenShift in OpenStack configuration
3) ACI configuration

The problem with scale testing is that there are limits on the physical
resources available. This means that some of the reasources must be
simulated, or physical resources must be more heavily loaded. Common
examples include fewer switches, servers, or resources on servers than
what is present in a customer installation.

# Limitations
Simulation may result in differences from the desired configuration.
For example, in order to simulate the required number of agents connected
to the fabric, multiple agents must be presented on the same switch port.
This triggers the use of remote endpoints, while the system being emulated
would not use remote endpoints.

This should be used with https://github.com/noironetworks/load-testing

The shell script in this repo does checks to make sure that the right
software is installed.

# Pre-requsites:
* Python
* Terraform
* Ansible

