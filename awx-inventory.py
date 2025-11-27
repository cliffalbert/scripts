#!/usr/bin/python3

import requests
import argparse
import sys
import json
import yaml

parser = argparse.ArgumentParser(description='Convert Ansible AWX/Tower Inventory to standard inventory')

parser.add_argument('--url', required=True, help='base url of AWX/Tower')
parser.add_argument('-u', '--username', help='username')
parser.add_argument('-p', '--password', help='password')
parser.add_argument('-i', '--inventory', help='New AWX Inventory')

args = parser.parse_args()

new_inventory = args.inventory

yaml_inventory = { new_inventory : { "children" : { } } }

r = requests.get('{}/api/v2/inventories/'.format(args.url), auth=(args.username, args.password))
for inventory in r.json()['results']:

    r = requests.get('{}/api/v2/inventories/{}/hosts'.format(args.url, inventory["id"]), auth=(args.username, args.password))

    if inventory["name"] == new_inventory:
        continue

    hosts = r.json()
    if 'results' in hosts:
        entries = hosts["results"]
    else:
        continue

    local_inventory =  { "hosts" : { } }

    for host in entries:
        yaml_vars = yaml.safe_load(host["variables"])
        print (json.dumps(host["variables"], indent=2))
        if yaml_vars:
            yaml_host = { "vars" : yaml_vars }
        else:
            yaml_host = { "description" : "Auto Added by AWX Inventory"}

        local_inventory["hosts"][host["name"]] = yaml_host

    yaml_inventory[new_inventory]["children"][inventory["name"]] = local_inventory


print(yaml.dump(yaml_inventory))
