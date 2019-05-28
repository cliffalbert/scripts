#!/usr/bin/python3

import pynetbox
import sys

nb = pynetbox.api(url='URL', token='TOKEN')

args = len(sys.argv)

if args > 1:
    
    wanted_prefix = sys.argv[1] + '/32'
    print ('\033[95mSearching for ' + wanted_prefix)

    single_prefix = nb.ipam.prefixes.filter(q=wanted_prefix)
    if len(single_prefix) < 1:
        sys.exit()
    my_pfx = single_prefix[0]
    fmt = "{:<20}{:<30}{:<40}{:<20}{:<40}"
    header = ("Prefix", "Tenant", "Description", "Role", "Site")
    my_pfx_tenant = 'None'
    my_pfx_role = 'None'
    my_pfx_site = 'None'
    my_vlan = 'None'
    my_vlan_group = 'None'
    my_vlan_description = 'None'

    if my_pfx.tenant:
        my_pfx_tenant = my_pfx.tenant.name
    if my_pfx.role:
        my_pfx_role = my_pfx.role.name
    if my_pfx.site:
        my_pfx_site = my_pfx.site.name
    if my_pfx.vlan:
        my_vlan = my_pfx.vlan.vid
        my_vlan_group = my_pfx.vlan.group.name

    print('\033[92m' + fmt.format(*header))
    print('\033[93m' + 
        fmt.format(
            str(my_pfx.prefix),
            my_pfx_tenant,
            my_pfx.description,
            my_pfx_role,
            my_pfx_site,
        )
    )
    single_address = nb.ipam.ip_addresses.filter(q=wanted_prefix)
    if len(single_address) > 0:
        my_addr = single_address[0]
        print ('\033[94m-------------------------------------------------------------------------------------')
        fmt = "{:<20}{:<30}{:<40}{:<10}{:<20}"
        header = ("Address", "Tenant", "Description", "VLAN ID", "VLAN Group")
        my_tenant = 'None'
        if my_addr.tenant:
            my_tenant = my_addr.tenant.name
      
        print('\033[92m' + fmt.format(*header))
        print('\033[93m' + 
            fmt.format(
                str(my_addr.address),
                my_tenant,
                my_addr.description,
                my_vlan,
                my_vlan_group,
                
            )
        )
    else:
        if my_pfx.vlan:
            my_vlan = my_pfx.vlan.vid
            my_vlan_group = my_pfx.vlan.group.name
            my_vlan_description = my_pfx.vlan.name
        fmt = "{:<20}{:<30}{:<40}"
        header = ("VLAN ID", "VLAN Group", "Description")
        print('\033[92m' + fmt.format(*header))
        print('\033[93m' +
                fmt.format(
                    my_vlan,
                    my_vlan_group,
                    my_vlan_description,
                )
        )




