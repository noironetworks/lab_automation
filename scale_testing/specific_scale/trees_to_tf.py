import argparse
import errno
import ipaddress
import json
import os
import uuid

import terraform_constants

DEF_EGRESS_RULES = [
    {'direction': 'egress',
     'ethertype': 'IPv4',
     'protocol': None,
     'remote_ip_prefix': '0.0.0.0/0',
     'remote_group_id': None},
    {'direction': 'egress',
     'ethertype': 'IPv6',
     'protocol': None,
     'remote_ip_prefix': '::/0',
     'remote_group_id': None}
]

DEF_INGRESS_RULES = [
    {'direction': 'ingress',
     'ethertype': 'IPv4',
     'protocol': None,
     'remote_ip_prefix': None},
    {'direction': 'egress',
     'ethertype': 'IPv6',
     'protocol': None,
     'remote_ip_prefix': None}
]


class ObjectTerraform(object):

    def __init__(self, hashtree_node, rn):
        self.hashtree_node = hashtree_node
        self.rn = rn
        self.project = self.get_tenant_rn(self.hashtree_node)
        # List of objects that are ready for rendering
        # into terraform.
        self.terraform_stack = []
        # We put things here if we need other
        # resources to fully render the template
        self.deferred_stack = []

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        if (self.project == other.project and self.rn == other.rn):
            return True
        else:
            return False

    def render_tf(self):
        """Render object into terraform

        Use the Terraform parser's state to create terraform
        scripts.
        """
        return ''

    def resolve(self, tf_obj_list):
        """Resolve terraform renderer state

        Additional information from other terraform rendering
        objects may be needed to fully define this renderer's state.
        This method checks a list of passed renderer objects to see if
        any of them have the missing state, and if they do, return this
        object as resolved.

        The admin tenant ID is an optional argument, as some objects
        in the ACI common tenant are actually OpenStack admin tenant
        shared objects.
        """
        return []

    def parse_hashtree(self):
        """Parse the hashtree node and it's children

        If a given node has all the information needed,
        then return it in the terraform_stack objects.
        If it doesn't, add it to the deferrred_stack.

        If a given node has children, determine the next
        Terraform handle object to create for each child.
        Return a list of any objects that still need information
        before they can be rendered into terraform scripts.
        """
        return self.terraform_stack, self.deferred_stack

    def get_tenant_rn(self, opflex_object):
        return opflex_object['key'][0].split("|")[1]

    def get_type_and_rn(self, opflex_object):
        return opflex_object['key'][-1].split("|")


class TenantTerraform(ObjectTerraform):
    """Tenant Terraform

    Parse tenant MOs and render the terrform to create the
    corresponding project in OpenStack.
    """

    def __init__(self, hashtree_node, rn):
        super(TenantTerraform, self).__init__(hashtree_node, rn)
        self.tenant_terraform = terraform_constants.TENANT_TERRAFORM
        if self.project != 'common':
            self.name_alias = hashtree_node['metadata']['attributes']['nameAlias']
            self.description = hashtree_node['metadata']['attributes']['descr']

    def parse_hashtree(self):
        # Tenants are always fully specified
        self.terraform_stack.append(self)
        for opflex_obj in self.hashtree_node['_children']:
            obj_type, rn = self.get_type_and_rn(opflex_obj)
            if obj_type == 'fvAp' and rn == 'OpenStack':
                ap_tf = AppProfileTerraform(opflex_obj, rn)
                stack, deferred = ap_tf.parse_hashtree()
                self.terraform_stack.extend(stack)
                self.deferred_stack.extend(deferred)
            elif obj_type == 'fvBD' and 'net_' in rn:
                bd_tf = BridgeDomainTerraform(opflex_obj, rn)
                stack, deferred = bd_tf.parse_hashtree()
                self.terraform_stack.extend(stack)
                self.deferred_stack.extend(deferred)
            elif obj_type == 'hostprotPol':
                sg_tf = SecurityGroupTerraform(opflex_obj, rn)
                stack, deferred = sg_tf.parse_hashtree()
                self.terraform_stack.extend(stack)
                self.deferred_stack.extend(deferred)
            elif obj_type == 'l3extOut':
                l3out_tf = L3OutTerraform(opflex_obj, rn)
                stack, deferred = l3out_tf.parse_hashtree()
                self.terraform_stack.extend(stack)
                self.deferred_stack.extend(deferred)
        return self.terraform_stack, self.deferred_stack

    def render_tf(self):
        # First create the tenant terraaform
        tf_string = self.tenant_terraform % {
            'project': self.rn,
            'name_alias': self.name_alias,
            'description': self.description}
        return tf_string


class CommonTenantTerraform(ObjectTerraform):
    """Common Tenant Terraform

    Parse tenant MOs and render the terrform to create the
    corresponding project in OpenStack.
    """

    def __init__(self, hashtree_node, rn):
        super(CommonTenantTerraform, self).__init__(hashtree_node, rn)

    def parse_hashtree(self):
        self.terraform_stack.append(self)
        # Tenants are always fully specified
        for opflex_obj in self.hashtree_node['_children']:
            obj_type, rn = self.get_type_and_rn(opflex_obj)
            if obj_type == 'vzBrCP':
                rtr_tf = ContractTerraform(opflex_obj, rn)
                stack, deferred = rtr_tf.parse_hashtree()
                self.terraform_stack.extend(stack)
                self.deferred_stack.extend(deferred)
            elif obj_type == 'fvCtx':
                vrf_tf = VrfTerraform(opflex_obj, rn)
                stack, deferred = vrf_tf.parse_hashtree()
                self.terraform_stack.extend(stack)
                self.deferred_stack.extend(deferred)
            if obj_type == 'fvAp' and 'OpenStack' in rn:
                ap_tf = AppProfileTerraform(opflex_obj, rn)
                stack, deferred = ap_tf.parse_hashtree()
                self.terraform_stack.extend(stack)
                self.deferred_stack.extend(deferred)
            elif obj_type == 'fvBD' and 'net_' in rn:
                bd_tf = BridgeDomainTerraform(opflex_obj, rn)
                stack, deferred = bd_tf.parse_hashtree()
                self.terraform_stack.extend(stack)
                self.deferred_stack.extend(deferred)
            #elif obj_type == 'l3extOut' and 'net_' in rn:
            #    l3out_tf = L3OutTerraform(opflex_obj, rn)
            #    stack, deferred = l3out_tf.parse_hashtree()
            #    self.terraform_stack.extend(stack)
            #    self.deferred_stack.extend(deferred)
        return self.terraform_stack, self.deferred_stack

            
class AppProfileTerraform(ObjectTerraform):
    """"Application Profile Terraform

    We don't need to render anything for application profiles,
    so this class just navigates to the next level of the hierarchy.
    """
    def __init__(self, hashtree_node, rn):
        super(AppProfileTerraform, self).__init__(hashtree_node, rn)

    def parse_hashtree(self):
        # Appplication profiles don't map to any resource in
        # OpenStack, so we won't add anything to the list of
        # terraform stack objects for it. We do need to handle
        # the child objects below it.
        for opflex_obj in self.hashtree_node['_children']:
            obj_type, rn = self.get_type_and_rn(opflex_obj)
            if (obj_type == 'fvAEPg' and 'net_' in rn) or (
                    self.project == 'common' and 
                    opflex_obj['key'][-2].split('|')[1].startswith('EXT-')):
                net_tf = EndpointGroupTerraform(opflex_obj, rn)
                stack, deferred = net_tf.parse_hashtree()
                self.terraform_stack.extend(stack)
                self.deferred_stack.extend(deferred)
        return self.terraform_stack, self.deferred_stack


class EndpointGroupTerraform(ObjectTerraform):
    """Endpoint Group Terrform

    Create the OpenStack network resources, based
    on the EPG and its associated resources.
    """
    def __init__(self, hashtree_node, rn):
        super(EndpointGroupTerraform, self).__init__(hashtree_node, rn)
        self.name_alias = hashtree_node['metadata']['attributes']['nameAlias']
        self.network_terraform = terraform_constants.NETWORK_TERRAFORM

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        if (self.project == other.project and
                self.rn == other.rn and self.name_alias == other.name_alias):
            return True
        else:
            return False

    def parse_hashtree(self):
        self.terraform_stack.append(self)
        for opflex_obj in self.hashtree_node['_children']:
            obj_type, rn = self.get_type_and_rn(opflex_obj)
            if obj_type == 'fvRsCons' or obj_type == 'fvRsProv' and 'rtr_' in rn:
                contract_tf = ContractReferenceTerraform(opflex_obj, rn)
                stack, deferred = contract_tf.parse_hashtree()
                self.terraform_stack.extend(stack)
                self.deferred_stack.extend(deferred)
        return self.terraform_stack, self.deferred_stack

    def render_tf(self):
        # First render oruselves
        tf_string = self.network_terraform % {
            'project': self.project,
            'name': self.rn,
            'name_alias': self.name_alias
        }
        return tf_string


class ContractReferenceTerraform(ObjectTerraform):
    """Contract Reference Terrform

    Create the OpenStack router interface resources, based
    on the Contract references.
    """
    def __init__(self, hashtree_node, rn):
        super(ContractReferenceTerraform, self).__init__(hashtree_node, rn)
        self.name_alias = hashtree_node['metadata']['attributes']['tnVzBrCPName']
        # There is no UUID represntation of router interfaces in ACI. Generate one
        # so that we can reference it in our terraform.
        self.if_name = "rtr_if_" + str(uuid.uuid4())
        self.subnet = None
        self.router_interface_terraform = terraform_constants.ROUTER_INTERFACE_TERRAFORM

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        if (self.project == other.project and self.rn == other.rn and
                self.name_alias == other.name_alias and self.subnet == other.subnet):
            return True
        else:
            return False

    def same_network(self, subnet_tf):
        this_network = self.hashtree_node['key'][-2].split('|')[1]
        that_network = subnet_tf.hashtree_node['key'][-2].split('|')[1]
        if this_network == that_network:
            return True
        else:
            return False

    def parse_hashtree(self):
        self.deferred_stack.append(self)
        return self.terraform_stack, self.deferred_stack

    def resolve(self, tf_obj_list):
        # Find any matching contract for the contract reference,
        # and if there is a match, complete the deferred state.
        # Routers are a special case, as the contracts (which map
        # to a router) are in the common tenant. We delete the
        # deferred contract from the list and add it to our stack.
        for tf_obj in tf_obj_list:
            if isinstance(tf_obj, SubnetTerraform):
                # See if we need to match this subnet
                if self.same_network(tf_obj):
                    self.subnet = tf_obj.name
                    return True
        return False
 
    def render_tf(self):
        tf_string = self.router_interface_terraform % {
            'name': self.rn,
            'router_if_name': self.if_name,
            'subnet': self.subnet
        }
        return tf_string


class GatewayContractReferenceTerraform(ObjectTerraform):
    """Gateway Contract Reference Terrform

    Resolve the external network for a router, and provide
    a terraform reference to pre-existing external networks.
    """
    def __init__(self, hashtree_node, rn):
        super(GatewayContractReferenceTerraform, self).__init__(hashtree_node, rn)
        self.name_alias = self.rn
        network_name_vrf = self.hashtree_node['key'][-3].split('|')[1]
        self.network_name = network_name_vrf[:network_name_vrf.rfind('-')]
        self.sanitized_network_name = self.network_name.replace('.', '_')
        self.external_network_terraform = terraform_constants.EXTERNAL_NETWORK_TERRAFORM

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        if (self.project == other.project and self.rn == other.rn and
                self.name_alias == other.name_alias):
            return True
        else:
            return False

    def parse_hashtree(self):
        self.deferred_stack.append(self)
        return self.terraform_stack, self.deferred_stack

    def resolve(self, tf_obj_list):
        if self.project == 'common':
            return False
        return True

    def render_tf(self):
        tf_string = self.external_network_terraform % {
            'name': self.sanitized_network_name,
            'name_alias': self.sanitized_network_name,
            'project': 'admin'
        }
        return tf_string


class ContractTerraform(ObjectTerraform):
    """Contract  Terrform

    Create the OpenStack router resources, based
    on the Contractx .
    """
    def __init__(self, hashtree_node, rn):
        super(ContractTerraform, self).__init__(hashtree_node, rn)
        self.name_alias = hashtree_node['metadata']['attributes']['nameAlias']
        self.name = rn
        self.external_network = None

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        if (self.project == other.project and self.rn == other.rn and
                self.name_alias == other.name_alias and self.name == other.name):
            return True
        else:
            return False

    def parse_hashtree(self):
        # We have to defer routers until we know which
        # project owns them.
        self.deferred_stack.append(self)
        return self.terraform_stack, self.deferred_stack

    def resolve(self, tf_obj_list):
        # Find any matching contract reference for the contract,
        # and if there is a match, move it to the resolved list.
        project_resolved = False
        for tf_obj in tf_obj_list:
            if isinstance(tf_obj, ContractReferenceTerraform):
                # Resolve the project from the ContractReferenceTerraform
                if self.rn == tf_obj.rn:
                    self.project = tf_obj.project
                    project_resolved = True
            if isinstance(tf_obj, GatewayContractReferenceTerraform):
                # Resolve the external gateway and project from the
                # GatewayContractReferenceTerraform
                if self.rn == tf_obj.rn:
                    self.project = tf_obj.project
                    self.external_network = tf_obj.sanitized_network_name
                    project_resolved = True
        if project_resolved:
            return True
        else:
            return False
 
    def render_tf(self):
        if self.external_network:
            self.router_interface_terraform = terraform_constants.ROUTER_GW_TERRAFORM
            tf_string = self.router_interface_terraform % {
                'name': self.rn,
                'name_alias': self.name_alias,
                'external_network': self.external_network,
                'project': self.project
            }
            return tf_string
        else:
            self.router_interface_terraform = terraform_constants.ROUTER_TERRAFORM
            tf_string = self.router_interface_terraform % {
                'name': self.rn,
                'name_alias': self.name_alias,
                'project': self.project
            }
            return tf_string


class BridgeDomainTerraform(ObjectTerraform):
    """Bridge Domain Terrform

    Manage the OpenStack network resources, based
    on the BD and its associated resources.
    """
    def __init__(self, hashtree_node, rn):
        super(BridgeDomainTerraform, self).__init__(hashtree_node, rn)
        self.name_alias = hashtree_node['metadata']['attributes']['nameAlias']

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        if (self.project == other.project and
                self.rn == other.rn and self.name_alias == other.name_alias):
            return True
        else:
            return False

    def parse_hashtree(self):
        for opflex_obj in self.hashtree_node['_children']:
            obj_type, rn = self.get_type_and_rn(opflex_obj)
            if obj_type == 'fvRsCtx':
                # All VRF refs start on the deferred list
                vrf_tf = VrfRefTerraform(opflex_obj, rn)
                # We only want one address scope reference
                if not self.deferred_stack:
                    self.deferred_stack.append(vrf_tf)
                else:
                    for def_obj in self.deferred_stack:
                        if isinstance(def_obj, VrfRefTerraform) and (
                                def_obj.project != vrf_tf.project or
                                def_obj.rn != vrf_tf.rn or
                                def_obj.name_alias != vrf_tf.name_alias):
                            self.deferred_stack.extend(vrf_tf)
            elif obj_type == 'fvSubnet':
                subnet_tf = SubnetTerraform(opflex_obj, rn)
                stack, deferred = subnet_tf.parse_hashtree()
                self.deferred_stack.extend(deferred)
                self.terraform_stack.extend(stack)
        return self.terraform_stack, self.deferred_stack


class VrfTerraform(ObjectTerraform):
    """VRF Terrform

    Manage the OpenStack address scope resources, based
    on the VRF and its associated resources.

    VRFs are put on deferred resources, and are used to
    resolve address scopes and subnet pools.
    """
    def __init__(self, hashtree_node, rn):
        super(VrfTerraform, self).__init__(hashtree_node, rn)
        self.name = rn
        self.name_alias = hashtree_node['metadata']['attributes']['nameAlias']
        self.cidrs = None
        self.subnetpools = []
        self.subnet_pool_shared_terraform = terraform_constants.SUBNET_POOL_SHARED_TERRAFORM

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        if (self.project == other.project and self.rn == other.rn and
                self.name_alias == other.name_alias and self.name == other.anme):
            return True
        else:
            return False

    def parse_hashtree(self):
        self.deferred_stack.append(self)
        return self.terraform_stack, self.deferred_stack

    def resolve(self, tf_obj_list):
        for tf_obj in tf_obj_list:
            if isinstance(tf_obj, VrfRefTerraform):
                # Check if this VRF reference is for the same parent BD
                if self.rn == tf_obj.name_alias:
                    tf_obj.vrf = self.rn
                    return True
        return False

    def render_tf(self):
        tf_string = ''
        for pool in self.subnetpools:
            tf_string += self.subnet_pool_shared_terraform % {
                'name': pool.subnetpool_id,
                'project': 'admin',
                'name_alias': pool.subnetpool_id,
                'cidrs': str(ipaddress.ip_interface(pool.rn).network),
                'prefixlen': ipaddress.ip_interface(pool.rn).network.prefixlen,
                'as_name': pool.vrf_ref}
        return tf_string


class VrfRefTerraform(ObjectTerraform):
    """VRF Reference Terrform

    Manage the OpenStack address scope resources, based
    on the VRF and its associated resources.
    """
    def __init__(self, hashtree_node, rn):
        super(VrfRefTerraform, self).__init__(hashtree_node, rn)
        self.name_alias = hashtree_node['metadata']['attributes']['tnFvCtxName']
        self.as_terraform = terraform_constants.ADDRESS_SCOPE_TERRAFORM
        self.as_shared_terraform = terraform_constants.ADDRESS_SCOPE_SHARED_TERRAFORM
        self.vrf = None

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        if (self.project == other.project and
                self.rn == other.rn and self.name_alias == other.name_alias):
            return True
        else:
            return False

    def same_network(self, sub_ref_tf):
        this_network = self.hashtree_node['key'][-2].split('|')[1]
        that_network = sub_ref_tf.hashtree_node['key'][-2].split('|')[1]
        if this_network == that_network:
            return True
        else:
            return False

    def best_vrf(self, candidate_vrf, deferral):
        if not candidate_vrf:
            return deferral
        if candidate_vrf.project == 'common' and (
                deferral.project != 'common'):
            return deferral
        return candidate_vrf

    def parse_hashtree(self):
        self.deferred_stack.append(self)
        return self.terraform_stack, self.deferred_stack

    def resolve(self, tf_obj_list):
        # Find all matching VRFs by name, either in this tenant,
        # or in the common tenant
        remove_deferred = []
        # Address scopes are a special case, as the VRFs (which map
        # to address scopes) can either be in the common tenant, or
        # in a non-common tenant. If it's in the common tenant, then
        # this is a shared address scope, and we can only create a
        # reference to it, as terraform doesn't support resource
        # extensions (we need to pass the DN of the pre-existing VRF).
        #
        # If it's in our (non-common) tenant, then we can create the
        # address scope resource.
        candidate_vrf = None
        for tf_obj in tf_obj_list:
            if isinstance(tf_obj, VrfTerraform):
                # See if we match this VRF
                if self.name_alias == tf_obj.rn:
                    # Switch if this one is better (e.g. previous was
                    # in the common tenant, but this one is in ours).
                    candidate_vrf = self.best_vrf(candidate_vrf, tf_obj)
            elif isinstance(tf_obj, SubnetTerraform):
                # Set the VRF ref name in the Subnet
                if self.same_network(tf_obj):
                    tf_obj.vrf_ref = self.name_alias

        if candidate_vrf:
            self.project = candidate_vrf.project
            self.vrf = candidate_vrf
            return True
        else:
            return False

    def render_tf(self):
        tf_string = ''
        if 'common' not in self.project and 'DefaultVRF' not in self.name_alias:
            tf_string = self.as_terraform % {
                'project': self.project,
                'name': self.name_alias,
                'name_alias': self.name_alias
            }
        elif 'common' in self.project and 'UnroutedVRF' not in self.name_alias:
            tf_string = self.as_shared_terraform % {
                'project': 'admin',
                'name': self.name_alias,
                'name_alias': self.name_alias
            }
        return tf_string


class SubnetTerraform(ObjectTerraform):
    """Subnet Terrform

    Manage the OpenStack subnet resources, based
    on the subnet and its associated resources.

    Subnets have to go on the deferral list, since we can't
    guarantee any ordering with respect to its peer MO, the
    VRF context reference.

    Once we get the VRF context, if it's in the common tenant,
    then we can't use terraform to create the address scope,
    since terraform doesn't support passing resource extensions,
    which would be needed to provide the DN of the VRF in ACI.
    """
    def __init__(self, hashtree_node, rn):
        super(SubnetTerraform, self).__init__(hashtree_node, rn)
        # No UUID representation in ACI for subnets - just generate one to
        # use in our terraform.
        self.name = "sub_" + str(uuid.uuid4())
        self.name_alias = hashtree_node['metadata']['attributes']['nameAlias']
        self.network = self.hashtree_node['key'][-2].split('|')[1]
        self.cidr = ipaddress.ip_interface(self.rn).network
        self.vrf = None
        self.vrf_ref = None
        self.subnetpool_id = None
        self.subnet_terraform = terraform_constants.SUBNET_TERRAFORM
        self.subnet_from_pool_terraform = terraform_constants.SUBNET_FROM_POOL_TERRAFORM

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        if (self.project == other.project and self.name == other.name and
                self.rn == other.rn and self.name_alias == other.name_alias):
            return True
        else:
            return False

    def same_network(self, vrf_ref_tf):
        that_network = vrf_ref_tf.hashtree_node['key'][-2].split('|')[1]
        if self.network == that_network:
            return True
        else:
            return False

    def parse_hashtree(self):
        self.deferred_stack.append(self)
        return self.terraform_stack, self.deferred_stack

    def resolve(self, tf_obj_list):
        # Find the matching peer VRF reference. It will either
        # bin our tenant or in the common tenant. If it's in
        # the common tenant, then there must be a shared
        # subnetpool in use, which also reports to a shared
        # vrf (we assume all subnetpools are used with address
        # scopes for now).
        for tf_obj in tf_obj_list:
            if isinstance(tf_obj, VrfRefTerraform):
                # Check if this VRF reference is for the same parent BD
                if self.same_network(tf_obj):
                    if tf_obj.vrf:
                        self.vrf = tf_obj.vrf
                    self.vrf_ref = tf_obj.name_alias
            elif self.vrf_ref and isinstance(tf_obj, VrfTerraform):
                if self.vrf_ref == tf_obj.rn:
                    self.vrf = tf_obj
        if self.vrf_ref:
            if self.vrf and self.vrf.project == 'common':
                self.subnetpool_id = "subp_" + str(uuid.uuid4())
                self.vrf.subnetpools.append(self)
            return True
        else:
            return False

    def render_tf(self):
        # Now handle our rendering
        if self.subnetpool_id:
            tf_string = self.subnet_from_pool_terraform % {
                'project': self.project,
                'name': self.name,
                'subnetpool_id': self.subnetpool_id,
                'network': self.hashtree_node['key'][-2].split('|')[1],
                'cidr': str(self.cidr),
                'name_alias': self.name_alias
            }
        else:
            tf_string = self.subnet_terraform % {
                'project': self.project,
                'name': self.name,
                'network': self.hashtree_node['key'][-2].split('|')[1],
                'cidr': str(self.cidr),
                'name_alias': self.name_alias
            }
        return tf_string


class L3OutTerraform(ObjectTerraform):
    """"L3 Outside Policy Terraform

    We don't need to render anything for L3 out policies,
    so this class just navigates to the next level of the hierarchy.
    """
    def __init__(self, hashtree_node, rn):
        super(L3OutTerraform, self).__init__(hashtree_node, rn)

    def parse_hashtree(self):
        # L3 Out policiesdon't map to any resource in
        # OpenStack, so we won't add anything to the list of
        # terraform stack objects for it. We do need to handle
        # the child objects below it.
        for opflex_obj in self.hashtree_node['_children']:
            obj_type, rn = self.get_type_and_rn(opflex_obj)
            if obj_type == 'l3extInstP':
                net_tf = L3OutInstpTerraform(opflex_obj, rn)
                stack, deferred = net_tf.parse_hashtree()
                self.terraform_stack.extend(stack)
                self.deferred_stack.extend(deferred)
        return self.terraform_stack, self.deferred_stack


class L3OutInstpTerraform(ObjectTerraform):
    """"L3 Outside Policy External EPG Terraform

    We don't need to render anything for L3 out policies,
    so this class just navigates to the next level of the hierarchy.
    """
    def __init__(self, hashtree_node, rn):
        super(L3OutInstpTerraform, self).__init__(hashtree_node, rn)

    def parse_hashtree(self):
        self.deferred_stack.append(self)
        for opflex_obj in self.hashtree_node['_children']:
            obj_type, rn = self.get_type_and_rn(opflex_obj)
            if obj_type == 'fvRsCons' or obj_type == 'fvRsProv':
                contract_tf = GatewayContractReferenceTerraform(opflex_obj, rn)
                stack, deferred = contract_tf.parse_hashtree()
                self.terraform_stack.extend(stack)
                self.deferred_stack.extend(deferred)
            #if obj_type == 'l3extRsEctx':
            #    contract_tf = GatewayContractReferenceTerraform(opflex_obj, rn)
            #    stack, deferred = contract_tf.parse_hashtree()
            #    self.terraform_stack.extend(stack)
            #    self.deferred_stack.extend(deferred)
        return self.terraform_stack, self.deferred_stack



class SecurityGroupTerraform(ObjectTerraform):
    """Security Group Terrform

    Manage the OpenStack security group resources, based
    on the hostprotPol and its associated resources.
    """
    def __init__(self, hashtree_node, rn):
        super(SecurityGroupTerraform, self).__init__(hashtree_node, rn)
        self.name = 'sg_' + rn
        self.name_alias = hashtree_node['metadata']['attributes']['nameAlias']

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        if (self.project == other.project and self.name == other.name and
                self.rn == other.rn and self.name_alias == other.name_alias):
            return True
        else:
            return False

    def parse_hashtree(self):
        self.terraform_stack.append(self)
        for opflex_obj in self.hashtree_node['_children']:
            obj_type, rn = self.get_type_and_rn(opflex_obj)
            if obj_type == 'hostprotSubj':
                sgs_tf = SecurityGroupSubjectTerraform(opflex_obj, rn)
                stack, deferred = sgs_tf.parse_hashtree()
                self.deferred_stack.extend(deferred)
                self.terraform_stack.extend(stack)
        return self.terraform_stack, self.deferred_stack

    def render_tf(self):
        # Now handle our rendering
        if self.name_alias == 'default':
            self.security_group_terraform = terraform_constants.SECURITY_GROUP_EXISTING_TERRAFORM
        else:
            self.security_group_terraform = terraform_constants.SECURITY_GROUP_TERRAFORM
        tf_string = self.security_group_terraform % {
            'project': self.project,
            'name': self.name,
            'name_alias': self.name_alias
        }
        return tf_string


class SecurityGroupSubjectTerraform(ObjectTerraform):
    """Security Group Subject Terrform

    Manage the OpenStack security group resources, based
    on the hostprotPol and its associated resources.
    """
    def __init__(self, hashtree_node, rn):
        super(SecurityGroupSubjectTerraform, self).__init__(hashtree_node, rn)
        self.name = rn

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        if (self.project == other.project and
                self.name == other.name and self.rn == other.rn):
            return True
        else:
            return False

    def parse_hashtree(self):
        for opflex_obj in self.hashtree_node['_children']:
            obj_type, rn = self.get_type_and_rn(opflex_obj)
            if obj_type == 'hostprotRule':
                sgr_tf = SecurityGroupRuleTerraform(opflex_obj, rn)
                stack, deferred = sgr_tf.parse_hashtree()
                self.terraform_stack.extend(stack)
                self.deferred_stack.extend(deferred)
        return self.terraform_stack, self.deferred_stack


class SecurityGroupRuleTerraform(ObjectTerraform):
    """Security Group Rule Terrform

    Manage the OpenStack security group rule resources, based
    on the hostprotRule and its associated resources. The rules
    go on the deferred list, as we need to know the type of rule
    to render.
    """
    def __init__(self, hashtree_node, rn):
        super(SecurityGroupRuleTerraform, self).__init__(hashtree_node, rn)
        self.name = 'sgr_' + rn
        self.direction = hashtree_node['metadata']['attributes']['direction']
        self.ethertype = hashtree_node['metadata']['attributes']['ethertype']
        self.protocol = hashtree_node['metadata']['attributes']['protocol']
        self.from_port = hashtree_node['metadata']['attributes']["fromPort"]
        self.to_port = hashtree_node['metadata']['attributes']["toPort"]
        self.icmp_type = hashtree_node['metadata']['attributes']["icmpType"]
        self.icmp_code = hashtree_node['metadata']['attributes']["icmpCode"]
        self.sec_group_id = 'sg_' + self.hashtree_node['key'][-3].split('|')[1]
        self.tf_type = None
        self.remote_group_id = None
        self.remote_ip_prefix = None
        self.security_group_rule_terraform = None

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        if (self.project == other.project and self.name == other.name and
                self.rn == other.rn and self.name_alias == other.name_alias):
            return True
        else:
            return False

    def parse_hashtree(self):
        self.deferred_stack.append(self)
        for opflex_obj in self.hashtree_node['_children']:
            obj_type, rn = self.get_type_and_rn(opflex_obj)
            if obj_type == 'hostprotRule':
                sgr_tf = SecurityGroupRule(opflex_obj, rn)
                stack, deferred = sgr_tf.parse_hashtree()
                self.terraform_stack.extend(stack)
                self.deferred_stack.extend(deferred)
        return self.terraform_stack, self.deferred_stack

    def _is_default_sg_rule(self):
        for rule in DEF_EGRESS_RULES:
            if (self.direction == rule['direction'] and
                    self.ethertype == rule['ethertype'] and
                    self.protocol == rule['protocol'] and
                    self.remote_ip_prefix == rule['remote_ip_prefix'] and
                    self.remote_group_id == rule['remote_group_id']):
                return True
        for rule in DEF_INGRESS_RULES:
            if (self.direction == rule['direction'] and
                    self.ethertype == rule['ethertype'] and
                    self.protocol == rule['protocol'] and
                    self.remote_ip_prefix == rule['remote_ip_prefix'] and
                    self.remote_group_id == self.sec_group_id):
                return True
        return False

    def resolve(self, tf_obj):
        if isinstance(tf_obj, dict):
            self.ethertype = tf_obj['Ethertype']
            self.protocol = tf_obj['IP Protocol']
            # Fix min/max port range (APIC converts them to
            # strings, some of which won't work in OpenStack)
            # If ICMP, then we accept what ACI has.
            if tf_obj['Remote Security Group']:
                self.remote_group_id = 'sg_' + tf_obj['Remote Security Group']
                if self.protocol == None:
                    self.security_group_rule_terraform = terraform_constants.SECURITY_GROUP_RULE_TERRAFORM_NO_PROTO_R_SG
                elif tf_obj['Port Range']:
                    if 'type' not in tf_obj['Port Range']:
                        self.from_port, self.to_port = tf_obj['Port Range'].split(':')
                    else:
                        pass

                    self.security_group_rule_terraform = terraform_constants.SECURITY_GROUP_RULE_TERRAFORM_PORTS_R_SG
                else:
                    self.to_port = None
                    self.from_port = None
                    self.security_group_rule_terraform = terraform_constants.SECURITY_GROUP_RULE_TERRAFORM_NO_PORTS_R_SG
            else:
                self.remote_ip_prefix = tf_obj['IP Range']
                if self.protocol == None:
                    self.security_group_rule_terraform = terraform_constants.SECURITY_GROUP_RULE_TERRAFORM_NO_PROTO_R_IP
                elif tf_obj['Port Range']:
                    if 'type' not in tf_obj['Port Range']:
                        self.from_port, self.to_port = tf_obj['Port Range'].split(':')
                    else:
                        pass
                    self.security_group_rule_terraform = terraform_constants.SECURITY_GROUP_RULE_TERRAFORM_PORTS_R_IP
                else:
                    self.to_port = None
                    self.from_port = None
                    self.security_group_rule_terraform = terraform_constants.SECURITY_GROUP_RULE_TERRAFORM_NO_PORTS_R_IP
            # We exclude the standard default security group rules
            if self._is_default_sg_rule():
                return False
            else:
                return True
        elif isinstance(tf_obj, list):
            for obj in tf_obj:
                if isinstance(obj, SecurityGroupTerraform) and self.sec_group_id == obj.name:
                    if obj.name_alias == 'default':
                        self.tf_type = 'data'
                    else:
                        self.tf_type = 'resource'
            return False
        else:
            return False

    def render_tf(self):
        # Now handle our rendering based on template type
        if (self.security_group_rule_terraform == terraform_constants.SECURITY_GROUP_RULE_TERRAFORM_PORTS_R_SG or
                self.security_group_rule_terraform == terraform_constants.SECURITY_GROUP_RULE_TERRAFORM_NO_PROTO_R_SG or
                self.security_group_rule_terraform == terraform_constants.SECURITY_GROUP_RULE_TERRAFORM_NO_PORTS_R_SG):
            tf_string = self.security_group_rule_terraform % {
                'tf_type': self.tf_type,
                'project': self.project,
                'name': self.name,
                'direction': self.direction,
                'ethertype': self.ethertype,
                'protocol': self.protocol,
                'min_port': self.from_port,
                'max_port': self.to_port,
                'remote_group_id': self.remote_group_id,
                'sec_group_id': self.sec_group_id
            }
        elif (self.security_group_rule_terraform == terraform_constants.SECURITY_GROUP_RULE_TERRAFORM_PORTS_R_IP or
                self.security_group_rule_terraform == terraform_constants.SECURITY_GROUP_RULE_TERRAFORM_NO_PROTO_R_IP or
                self.security_group_rule_terraform == terraform_constants.SECURITY_GROUP_RULE_TERRAFORM_NO_PORTS_R_IP):
            tf_string = self.security_group_rule_terraform % {
                'tf_type': self.tf_type,
                'project': self.project,
                'name': self.name,
                'direction': self.direction,
                'ethertype': self.ethertype,
                'protocol': self.protocol,
                'min_port': self.from_port,
                'max_port': self.to_port,
                'remote_ip_prefix': self.remote_ip_prefix,
                'sec_group_id': self.sec_group_id
            }
        return tf_string


class PortTerraform(ObjectTerraform):
    def __init__(self, hashtree_node, rn):
        super(PortTerraform, self).__init__(hashtree_node, rn)

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        if (self.project == other.project and
                self.name == other.name and self.rn == other.rn):
            return True
        else:
            return False

    def parse_hashtree(self):
        pass



class TerraformManager(object):
    def __init__(self, config_tree_filename, monitor_tree_filename,
                 ports_filename, sgs_filename, cloud_ip, cloud_user, cloud_password):
        self.config_tree_filename = config_tree_filename
        self.monitor_tree_filename = monitor_tree_filename
        self.ports_filename = ports_filename
        self.sgs_filename = sgs_filename
        self.cloud_ip = cloud_ip
        self.cloud_user = cloud_user
        self.cloud_password = cloud_password
        self.sg_rules_by_id = {}
        self.json_sgs = []
        self.json_ports = []
        self.json_policy = []
        self.ports_by_tenant = {}
        self.ports_by_network = {}
        self.crud_ports_by_tenant = {}
        self.unconnected_subnets = {}
        self.terraform_admin_project = terraform_constants.ADMIN_TENANT_TERRAFORM
        self.terraform_provider_template = terraform_constants.TERRAFORM_PROVIDER

    def _get_sgs_json(self):
        if not self.sgs_filename:
            return
        with open(self.sgs_filename, 'r') as fd:
            self.json_sgs = json.load(fd)
        for sgr in self.json_sgs:
            self.sg_rules_by_id[sgr['ID']] = sgr

    def _get_ports_json(self):
        if not self.ports_filename:
            return
        with open(self.ports_filename, 'r') as fd:
            self.json_ports = json.load(fd)
        self._parse_ports()

    def _parse_ports(self):
        for port in self.json_ports:
            self.ports_by_tenant.setdefault(port['project_id'], []).append(port)
            self.ports_by_network.setdefault(port['network_id'], []).append(port)
            owner =  port['device_owner']
            if owner == '':
                owner = None
            elif owner.startswith('compute'):
                owner = 'compute'
            else:
                continue
            # Fix things about the port that terraform
            # doesn't like
            if port['admin_state_up'] == True:
                port['admin_state_up'] = 'true'
            elif port['admin_state_up'] == False:
                port['admin_state_up'] = 'false'
            if port['name'] == '':
                port['name'] = port['dns_assignment'][0]['hostname'] 
            self.crud_ports_by_tenant.setdefault('prj_' + port['project_id'], []).append(port)

    def infer_cidr(self, ip_list):
        prefixlen = 32
        cidr = ipaddress.ip_interface(ip_list[0] + '/' + str(prefixlen)).network
        for ip in ip_list:
            while prefixlen > 16:
                ip_addr = ipaddress.ip_address(ip)
                if ip_addr in cidr:
                    break
                prefixlen -= 1
                cidr = ipaddress.ip_interface(ip_list[0] + '/' + str(prefixlen)).network
        return cidr

    def resolve_dup_portnames(self, tenant):
        port_names = {}
        dup_ports = set()
        for port in self.crud_ports_by_tenant.get(tenant, []):
            if port['name'] in port_names.keys():
                dup_ports.add(port['name'])
            else:
                port_names.setdefault(port['name'], []).append(port)
        for dup in dup_ports:
            for idx, port in enumerate(port_names[dup]):
                port['name'] = port['name'] + "-%s" % str(idx)

    def resolve_port_subnets(self, tenant, subnet_stack):
        tf_string = ''
        unresolved_subnets = {}
        for port in self.crud_ports_by_tenant.get(tenant, []):
            network = 'net_' + port['network_id']
            for entry in port['fixed_ips']:
                resolved = False
                for subnet in subnet_stack:
                    if subnet.network == network:
                        if ipaddress.ip_address(entry['ip_address']) in subnet.cidr:
                            entry['subnet_id'] = subnet.name[4:]
                            resolved = True
                if not resolved:
                    # This is an unconnected subnet - keep track of it for later
                    unresolved = unresolved_subnets.setdefault(entry['subnet_id'], {})
                    unresolved['project_id'] = port['project_id']
                    unresolved['network_id'] = port['network_id']
                    unresolved.setdefault('ip_addresses', []).append(entry['ip_address'])

        # Now determine the CIDRs from the list of IPs, and add to our
        # master list of unconnected subnets.
        for subnet_id, sub_dict in unresolved_subnets.items():
            cidr = self.infer_cidr(sub_dict['ip_addresses'])
            entry = self.unconnected_subnets.setdefault(subnet_id, {})
            entry['cidr']= cidr
            entry['project_id']= sub_dict['project_id']
            entry['network_id']= sub_dict['network_id']
            self.unconnected_subnets[subnet_id].update(entry)
            sub_name = "sub_" + subnet_id
            tf_string += terraform_constants.SUBNET_TERRAFORM % {
                'project': 'prj_' + entry['project_id'],
                'name': sub_name,
                'network': 'net_' + entry['network_id'],
                'cidr': str(entry['cidr']),
                'name_alias': sub_name
            }
        return tf_string

    def render_port_tf(self, port_dict, subnet_stack, default_sg):
        tf_string = ''
        device_owner = port_dict['device_owner']
        # Only consider ports for VMs or AAPs, etc.
        if device_owner == '' or device_owner.startswith('compute:'):
            tf_string += terraform_constants.PORT_PART1_TERRAFORM % port_dict
            security_groups = port_dict['security_group_ids']
            if len(security_groups) == 0:
                tf_string += terraform_constants.PORT_NO_SECGROUP_TERRAFORM
            else:
                tf_string += terraform_constants.PORT_START_SECGROUP_TERRAFORM
                for sg in security_groups[:-1]:
                    if sg == default_sg:
                        tf_string += terraform_constants.PORT_DEFAULT_SECGROUP_TERRAFORM % sg
                    else:
                        tf_string += terraform_constants.PORT_SECGROUP_TERRAFORM % sg
                if security_groups[-1] == default_sg:
                    tf_string += terraform_constants.PORT_DEFAULT_LAST_SECGROUP_TERRAFORM % security_groups[-1]
                else:
                    tf_string += terraform_constants.PORT_LAST_SECGROUP_TERRAFORM % security_groups[-1]
            for entry in port_dict['fixed_ips']:
                tf_string += terraform_constants.PORT_FIXED_IP_TERRAFORM % entry
            for entry in port_dict['allowed_address_pairs']:
                tf_string += terraform_constants.PORT_AAPS_TERRAFORM % entry
            tf_string += terraform_constants.PORT_PART2_TERRAFORM % port_dict

        return tf_string

    def _get_policy_json(self, filename):
        with open(filename, 'r') as fd:
            self.json_policy = json.load(fd)

    def create_terraform(self):
        provider_tf = self.terraform_provider_template % {
                'username': self.cloud_user,
                'password': self.cloud_password,
                'ip': self.cloud_ip
        }
        admin_tf = None
        common_stack = []
        common_deferrals = []

        self._get_sgs_json()
        self._get_ports_json()

        # Collect the monitored tree objects for rendering.
        # The only object we care about here are the VRFs,
        # which are deferred objects.
        self._get_policy_json(self.monitor_tree_filename)
        for tree_root in self.json_policy:
            obj_type, rn = tree_root['key'][-1].split("|")
            # For monitored, we only care about the common tenant
            if obj_type == 'fvTenant' and rn == 'common':
                tenant_tf = CommonTenantTerraform(tree_root, rn)
                _, deferred = tenant_tf.parse_hashtree()
                common_deferrals.extend(deferred)

        self._get_policy_json(self.config_tree_filename)
        # First find out the admin project. The tenant ID is
        # needed to be able to resolve renderers in other projects.
        for tree_root in self.json_policy:
            obj_type, rn = tree_root['key'][-1].split("|")
            # We only care about state under tenants
            if obj_type == 'fvTenant' and rn != 'common':
                name_alias = tree_root['metadata']['attributes']['nameAlias']
                if name_alias == 'admin':
                    admin_tf = self.terraform_admin_project % {
                            'description': 
                                tree_root['metadata']['attributes']['descr']
                    }

        # Collect the configuration tree objects for rendering.
        for tree_root in self.json_policy:
            obj_type, rn = tree_root['key'][-1].split("|")
            # We only care about state under tenants
            if obj_type == 'fvTenant':
                if rn == 'common':
                    tenant_tf = CommonTenantTerraform(tree_root, rn)
                else:
                    tenant_tf = TenantTerraform(tree_root, rn)
                stack, deferrals = tenant_tf.parse_hashtree()
                # We save the common tenant state separately
                # (combined with the monitored state earlier),
                # since that needs to be resolved across all
                # tenants.
                if rn == 'common':
                    common_stack.extend(stack)
                    common_deferrals.extend(deferrals)
                    continue

                # Check to see if anything from the common tenant
                # tenant unresolved resources can be resolved against
                # this tenant's resources.
                moved = []
                for deferral in common_deferrals:
                    if deferral.resolve(stack):
                        #moved.append(deferral)
                        stack.append(deferral)
                    elif deferral.resolve(deferrals):
                        #moved.append(deferral)
                        stack.append(deferral)

                # Check to see if anything from the common tenant
                # tenant resolved resources can be resolved against
                # this tenant's unresolved resources.
                for stack_obj in common_stack:
                    if stack_obj.resolve(deferrals):
                        stack.append(stack_obj)
                    elif stack_obj.resolve(stack):
                        stack.append(stack_obj)

                # Check to see if anything can be resolved from the
                # common tenant unresolved resources
                moved = []
                for deferral in deferrals:
                    if deferral.resolve(common_deferrals):
                        stack.append(deferral)
                        moved.append(deferral)
                for tf_obj in moved:
                    try:
                        deferrals.remove(tf_obj)
                    except ValueError:
                        pass

                # Check to see if anything can be resolved against the
                # common tenant resolved resources.
                moved = []
                for deferral in deferrals:
                    resolved = deferral.resolve(common_stack)
                    if resolved:
                        stack.append(deferral)
                        moved.append(deferral)
                for tf_obj in moved:
                    deferrals.remove(tf_obj)

                # Now check to see if anything can be resolved from
                # this tenant's resolved state.
                moved = []
                for deferral in deferrals:
                    resolved = deferral.resolve(stack)
                    if resolved:
                        stack.append(deferral)
                        moved.append(deferral)
                for tf_obj in moved:
                    deferrals.remove(tf_obj)

                # Now see if any of the deferrals can resolve each other,
                # or if security group rules, if they can be resolved from
                # additional configuration files.
                for deferral in deferrals:
                    if isinstance(deferral, SecurityGroupRuleTerraform):
                        sg_id = deferral.rn
                        resolved = deferral.resolve(self.sg_rules_by_id.get(sg_id))
                    else:
                        resolved = deferral.resolve(deferrals)
                    if resolved:
                        stack.append(deferral)

                # Identify any duplicates (could just use Pandas, but hey...)
                dup_indeces = set()
                for index, tf_ref in enumerate(stack):
                    for dup_idx, tf_compare in enumerate(stack[index + 1::]):
                        # Only compare objects of the same type:
                        if tf_ref.__class__ != tf_compare.__class__:
                            continue
                        if tf_ref == tf_compare:
                            dup_indeces.add(index + 1 + dup_idx)

                # Keep separte list of subnets on the stack (needed to resolve the ports)
                subnet_stack = []
                # Keep track of default security group
                default_sg = None
                tf = ''
                for index, tf_obj in enumerate(stack):
                    if isinstance(tf_obj, SubnetTerraform):
                        subnet_stack.append(tf_obj)
                    if isinstance(tf_obj, SecurityGroupTerraform):
                        if tf_obj.name_alias == 'default':
                            default_sg = tf_obj.name[3:]
                    if index in list(dup_indeces):
                        continue
                    # For non-admin tenants, add a reference to the admin tenant
                    if isinstance(tf_obj, TenantTerraform) and tf_obj.rn != 'admin':
                        tf += admin_tf
                    tf += tf_obj.render_tf()
                # Resolve any unresolved subnets
                tf += self.resolve_port_subnets(tenant_tf.rn, subnet_stack)
                # Now add in the ports for this project
                self.resolve_dup_portnames(tenant_tf.rn)
                for port in self.crud_ports_by_tenant.get(tenant_tf.rn, []):
                    tf += self.render_port_tf(port, subnet_stack, default_sg)
                project_dir = os.getcwd() + '/' +  rn
                try:
                    print("Making directory %s" % project_dir)
                    os.mkdir(project_dir)
                except OSError as e:
                    if e.errno == errno.EEXIST:
                        print('Directory not created.')
                    else:
                        raise
                with open(project_dir + '/' + rn + ".tf", "w+") as fd:
                    fd.write(provider_tf)
                    fd.write(tf)

def run():
    parser = argparse.ArgumentParser(
            description='OpenStack Terraform Configuration Generator')
    parser.add_argument('--cloud-ip',default="10.30.120.201",
            help='IP Address of OpenStack horizon.')
    parser.add_argument('--cloud-user',default="admin",
            help='User of the OpenStack cloud')
    parser.add_argument('--cloud-password',default="noir0123",
            help='Password for theUser of the OpenSTack cloud')
    parser.add_argument('--config-tree-file',
            help='Full path to the configured state hashtree file')
    parser.add_argument('--monitor-tree-file',
            help='Full path to the monitored state hashtree file')
    parser.add_argument('--ports-file',
            help='Full path to the file containing the ports in OpenStack')
    parser.add_argument('--security-groups-file',
            help='Full path to the file with security group data in OpenStack')

    args = parser.parse_args()
    manager = TerraformManager(args.config_tree_file, args.monitor_tree_file,
            args.ports_file, args.security_groups_file, args.cloud_ip,
            args.cloud_user, args.cloud_password)
    manager.create_terraform()

if __name__ == '__main__':
    run()
