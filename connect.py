"""Create and manage virtual machines.
 
The following environment vars are set in the .env file:
 
AZURE_TENANT_ID: your Azure Active Directory tenant id or domain
AZURE_CLIENT_ID: your Azure Active Directory Application Client ID
AZURE_CLIENT_SECRET: your Azure Active Directory Application Secret
AZURE_SUBSCRIPTION_ID: your Azure Subscription Id
"""
import os
import traceback
import json
import threading
import time
 
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.identity import ClientSecretCredential
from azure.mgmt.compute.models import DiskCreateOption, InstanceViewTypes
 
from msrestazure.azure_exceptions import CloudError
 
from haikunator import Haikunator
 
from dotenv import load_dotenv

load_dotenv()

haikunator = Haikunator()
 
# Azure Datacenter
LOCATION = 'westeurope'
 
# Resource Group
GROUP_NAME = 'azure-virtualsy'
 
# Network
VNET_NAME = 'azure-virtualsy-vnet'
SUBNET_NAME = 'azure-virtualsy-subnet'
 
# VM
OS_DISK_NAME = 'azure-virtualsy-osdisk'
STORAGE_ACCOUNT_NAME = haikunator.haikunate(delimiter='')
 
IP_CONFIG_NAME = 'azure-virtualsy-ip-config'
NIC_NAME = 'azure-virtualsy-nic'
USERNAME = 'virtualuser'
PASSWORD = 'PasswordForMachine1'
VM_NAME = 'Virtualsy'


VM_REFERENCE = {
    'linux': {
        'publisher': 'Canonical',
        'offer': '0001-com-ubuntu-server-focal',
        'sku': '20_04-lts',
        'version': 'latest'
    },
    'windows': {
        'publisher': 'MicrosoftWindowsServer',
        'offer': 'WindowsServer',
        'sku': '2016-Datacenter',
        'version': 'latest'
    }
}
 
 
def get_credentials():
    subscription_id = os.environ['AZURE_SUBSCRIPTION_ID']
    credentials = ClientSecretCredential(
        client_id=os.environ['AZURE_CLIENT_ID'],
        client_secret=os.environ['AZURE_CLIENT_SECRET'],
        tenant_id=os.environ['AZURE_TENANT_ID']
    )
    return credentials, subscription_id

async def create_vm(resource_client, compute_client, network_client, os):
    try:
        # Try to get the VM by name
        compute_client.virtual_machines.get(GROUP_NAME, VM_NAME)

        print(f'\nVirtual Machine {VM_NAME} already exists.')
        return send_vm_info(network_client, compute_client)
        
    except Exception:
        # VM does not exist, create it
        if os == 'linux': 
            print('\nCreate Linux')
            create_linux(compute_client, network_client)
            return send_vm_info(network_client, compute_client)
            
            
        elif os == 'windows':
            print('\nCreate Windows')
            create_windows(compute_client, network_client)

            return send_vm_info(network_client, compute_client)

        else:
            print(f'\nInvalid OS type: {os}')

async def create_vm_async(os):
    credentials, subscription_id = get_credentials()
    resource_client = ResourceManagementClient(credentials, subscription_id)
    compute_client = ComputeManagementClient(credentials, subscription_id)
    network_client = NetworkManagementClient(credentials, subscription_id)
    
    # Create Resource group
    print('\nCreate Resource Group')
    resource_client.resource_groups.create_or_update(
        GROUP_NAME, {'location': LOCATION})
    
    # Create VM
    return await create_vm(resource_client, compute_client, network_client, os)

    

def send_vm_info(network_client, compute_client):
    virtual_machine = compute_client.virtual_machines.get(GROUP_NAME, VM_NAME)
    nic_id = virtual_machine.network_profile.network_interfaces[0].id
    nic = network_client.network_interfaces.get(GROUP_NAME, nic_id.split('/')[-1])

    # Get the public IP configuration
    public_ip_id = nic.ip_configurations[0].public_ip_address.id
    public_ip = network_client.public_ip_addresses.get(GROUP_NAME, public_ip_id.split('/')[-1])

    os_type = 'Linux' if virtual_machine.os_profile.linux_configuration else 'Windows'

    # get the VM
    vm = compute_client.virtual_machines.get(GROUP_NAME, VM_NAME, expand=InstanceViewTypes.instance_view)

    # retrieve the execution state
    execution_state = vm.instance_view.statuses[1].display_status


    vm = {
            'name': virtual_machine.name,
            'location': virtual_machine.location,
            'type': virtual_machine.type,
            'admin_username': USERNAME,
            'admin_password': PASSWORD,
            'resource_group_name': virtual_machine.id.split('/')[4],
            'vm_id': virtual_machine.vm_id,
            'public_ip': public_ip.ip_address,
            'os_type': os_type,
            'status': execution_state
        }

    json_vm = json.dumps(vm, indent=4)
    return json_vm
 
def create_windows(compute_client, network_client):
    try:
        # Create a NIC
        nic = create_nic(network_client)
        # Create Windows VM
        print('\nCreating Windows Virtual Machine')
        # Recycling NIC of previous VM
        vm_parameters = create_vm_parameters(nic.id, VM_REFERENCE['windows'])
        async_vm_creation = compute_client.virtual_machines.begin_create_or_update(
            GROUP_NAME, VM_NAME, vm_parameters)
        async_vm_creation.wait()

         # Tag the VM
        print('\nTag Virtual Machine')
        async_vm_update = compute_client.virtual_machines.begin_create_or_update(
            GROUP_NAME,
            VM_NAME,
            {
                'location': LOCATION,
                'tags': {
                    'who-rocks': 'python',
                    'where': 'on azure',
                }
            }
        )

        async_vm_update.wait()
        
        # Create a new thread to handle the VM deletion
        vm_deletion_thread = threading.Thread(target=delete_ressources_after_delay)
        vm_deletion_thread.start()

    except CloudError:
        print('A VM operation failed:\n{}'.format(traceback.format_exc()))
    else:
        print('All example operations completed successfully!')
 
 
def create_linux(compute_client, network_client):
    try:
        # Create a NIC
        nic = create_nic(network_client)

        # Create Linux VM
        print('\nCreating Linux Virtual Machine')
    
        vm_parameters = create_vm_parameters(nic.id, VM_REFERENCE['linux'])
        async_vm_creation = compute_client.virtual_machines.begin_create_or_update(
            GROUP_NAME, VM_NAME, vm_parameters)
        async_vm_creation.wait()
        
        # Tag the VM
        print('\nTag Virtual Machine')
        async_vm_update = compute_client.virtual_machines.begin_create_or_update(
            GROUP_NAME,
            VM_NAME,
            {
                'location': LOCATION,
                'tags': {
                    'who-rocks': 'python',
                    'where': 'on azure',
                }
            }
        )
        async_vm_update.wait()
 
        # Create managed data disk
        print('\nCreate (empty) managed Data Disk')
        async_disk_creation = compute_client.disks.begin_create_or_update(
            GROUP_NAME,
            'mydatadisk1',
            {
                'location': LOCATION,
                'disk_size_gb': 10,
                'creation_data': {
                    'create_option': DiskCreateOption.empty
                }
            }
        )
        data_disk = async_disk_creation.result()
 
        # Get the virtual machine by name
        print('\nGet Virtual Machine by Name')
        virtual_machine = compute_client.virtual_machines.get(
            GROUP_NAME,
            VM_NAME
        )
 
        # Attach data disk
        print('\nAttach Data Disk')
        virtual_machine.storage_profile.data_disks.append({
            'lun': 12,
            'name': 'mydatadisk1',
            'delete_option': 'Delete',
            'create_option': DiskCreateOption.attach,
            'managed_disk': {
                'id': data_disk.id
            }
        })
        async_disk_attach = compute_client.virtual_machines.begin_create_or_update(
            GROUP_NAME,
            virtual_machine.name,
            virtual_machine
        )
        async_disk_attach.wait()
         # Create a new thread to handle the VM deletion
        vm_deletion_thread = threading.Thread(target=delete_ressources_after_delay)
        vm_deletion_thread.start()
 

    except CloudError:
        print('A VM operation failed:\n{}'.format(traceback.format_exc()))
    else:
        print('All example operations completed successfully!')



 
def create_nic(network_client):
    """Create a Network Interface for a VM.
    """
    # Create VNet
    print('\nCreate Vnet')
    async_vnet_creation = network_client.virtual_networks.begin_create_or_update(
        GROUP_NAME,
        VNET_NAME,
        {
            'location': LOCATION,
            'address_space': {
                'address_prefixes': ['10.0.0.0/16']
            }
        }
    )
    async_vnet_creation.wait()
 
    # Create Subnet
    print('\nCreate Subnet')
    async_subnet_creation = network_client.subnets.begin_create_or_update(
        GROUP_NAME,
        VNET_NAME,
        SUBNET_NAME,
        {'address_prefix': '10.0.0.0/24'}
    )
    subnet_info = async_subnet_creation.result()
 
    # Create Public IP address
    print('\nCreate Public IP address')
    async_public_ip_creation = network_client.public_ip_addresses.begin_create_or_update(
        GROUP_NAME,
        'azure-virtualsy-public-ip',
        {
            'location': LOCATION,
            'sku': {
                'name': 'Standard'
            },
            'public_ip_allocation_method': 'Static',  # set to Static
            'dns_settings': {
                'domain_name_label': 'azure-virtualsy-dns'
            }
        }
    )
    public_ip_info = async_public_ip_creation.result()
 
 
    # Create NIC with public IP configuration
    print('\nCreate NIC with public IP configuration')
    async_nic_creation = network_client.network_interfaces.begin_create_or_update(
        GROUP_NAME,
        NIC_NAME,
        {
            'location': LOCATION,
            'ip_configurations': [{
                'name': IP_CONFIG_NAME,
                'subnet': {
                    'id': subnet_info.id
                },
                'public_ip_address': {
                    'id': public_ip_info.id
                }
            }]
        }
    )
 
    # Create Network Security Group
    print('\nCreate Network Security Group')
    async_nsg_creation = network_client.network_security_groups.begin_create_or_update(
        GROUP_NAME,
        'azure-virtualsy-nsg',
        {
            'location': LOCATION,
            'security_rules': [{
                'name': 'allow-ssh',
                'protocol': 'Tcp',
                'source_port_range': '*',
                'destination_port_range': '22',
                'source_address_prefix': '*',
                'destination_address_prefix': '*',
                'access': 'Allow',
                'priority': 100,
                'direction': 'Inbound'
            }]
        }
    )
    nsg_info = async_nsg_creation.result()
 
    # Associate NSG with network interface
    print('\nAssociate NSG with network interface')
    async_nic_update = network_client.network_interfaces.begin_create_or_update(
        GROUP_NAME,
        NIC_NAME,
        {
            'location': LOCATION,
            'network_security_group': {
                'id': nsg_info.id
            },
            'ip_configurations': [{
                'name': IP_CONFIG_NAME,
                'subnet': {
                    'id': subnet_info.id
                },
                'public_ip_address': {
                    'id': public_ip_info.id
                }
            }]
        }
    )
 
    # Create
    return async_nic_creation.result()
 
 
def create_vm_parameters(nic_id, vm_reference):
    """Create the VM parameters structure.
    """
    return {
        'location': LOCATION,
        'os_profile': {
            'computer_name': VM_NAME,
            'admin_username': USERNAME,
            'admin_password': PASSWORD,
            'delete_data_disks_on_termination': True, 
            'delete_os_disk_on_termination': True
        },
        'hardware_profile': {
            'vm_size': 'Standard_DS1_v2'
        },
        'storage_profile': {
            'image_reference': {
                'publisher': vm_reference['publisher'],
                'offer': vm_reference['offer'],
                'sku': vm_reference['sku'],
                'version': vm_reference['version']
            },
        },
        'network_profile': {
            'network_interfaces': [{
                'id': nic_id,
            }]
        },
    }



def startVm(compute_client):
    # Check if VM exists
    try:
        virtual_machine = compute_client.virtual_machines.get(GROUP_NAME, VM_NAME)
    except CloudError:
        print('Error: Virtual machine {} not found.'.format(VM_NAME))
        return
    
    # Start the VM
    print('\nStarting VM...')
    async_vm_start = compute_client.virtual_machines.start(GROUP_NAME, VM_NAME)
    async_vm_start.wait()
 
def stopVm(compute_client):
        # Check if VM exists
    try:
        virtual_machine = compute_client.virtual_machines.get(GROUP_NAME, VM_NAME)
    except CloudError:
        print('Error: Virtual machine {} not found.'.format(VM_NAME))
        return
    # Stop the VM
    print('\nStopping VM')
    async_vm_stop = compute_client.virtual_machines.power_off(GROUP_NAME, VM_NAME)
    async_vm_stop.wait()


def delete_ressources_after_delay():
    # Wait for 10 minutes
    time.sleep(600) 
    deleteRessources()

def deleteRessources():
    try:
        credentials, subscription_id = get_credentials()
        resource_client = ResourceManagementClient(credentials, subscription_id)
        # Delete Resource group and everything in it
        print('\nDelete Resource Group')
        delete_async_operation = resource_client.resource_groups.begin_delete(
            GROUP_NAME)
        delete_async_operation.wait()
        return "\nDeleted: {}".format(GROUP_NAME)
    except Exception:
        return 'error destroying the machine'





if __name__ == "__main__":
    connect('linux')