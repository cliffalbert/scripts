#!/usr/bin/python3

import pynetbox
import sys
import pprint

nb = pynetbox.api(url='URL', token='TOKEN')

pp = pprint.PrettyPrinter(indent=4)

args = len(sys.argv)

if args > 1:
    
    wanted_prefix = sys.argv[1] 
    print ('Searching for ' + wanted_prefix)

    single_prefix = nb.ipam.prefixes.filter(tenant=wanted_prefix)
    if len(single_prefix) < 1:
        sys.exit()
    fmt = "{:<30}{:<55}{:<20}"
    header = ("IP Range", "Description", "Role")
    print('' + fmt.format(*header))

    for my_pfx in single_prefix:
        my_pfx_tenant = 'None'
        my_pfx_role = 'None'
        my_pfx_site = 'None'
        my_vlan = 'None'
        my_vlan_group = 'None'
        my_vlan_description = my_pfx.description 
        my_vlan_provider = 'None'
        my_vlan_providerid = 'None'

        if my_pfx.tenant:
            my_pfx_tenant = my_pfx.tenant.name
        if my_pfx.role:
            my_pfx_role = my_pfx.role.name
        if my_pfx.site:
            my_pfx_site = my_pfx.site.name
        if my_pfx.vlan:
            my_vlan = my_pfx.vlan.vid
            my_vlan_group = my_pfx.vlan.group.name

        if my_pfx.vlan:
            my_vlan = my_pfx.vlan.vid
            my_vlan_uid = my_pfx.vlan.id
            my_vlan_group = my_pfx.vlan.group.name
            my_vlan_description = my_pfx.vlan.name
            my_vlan_obj = my_pfx.vlan.custom_fields
            if my_vlan_obj['provider']:
                my_vlan_provider = my_vlan_obj['provider']['label']
                my_vlan_providerid = my_vlan_obj['provider_id']

        print('' +
            fmt.format(
                str(my_pfx.prefix),
                my_vlan_description,
                str(my_pfx_role),
            )
        )




