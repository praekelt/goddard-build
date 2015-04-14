# Goddard Build

## About

Takes care of "building" (provisioning) the nodes. The Hub server connects over SSH and makes use of http://www.ansible.com.

The playbook only touches application specific services to make sure the node is always connected.

The script does a few steps:

* Updates hostname
* Updates to correct timezone (*SAST*)
* Updates the package list
* Safe Upgrades all the security updates
* Installs needed debs/tools
* Installs and configures Docker
* Adds all the rquired images to Docker
* Installs and configures NGINX for docker and local pages
* Adds local data files that allow the Node to read it's own installed apps

## Running

The inventory of all the nodes is pulled from a database table. This table contains all the configured nodes and their details.

### To run:

````bash
ansible-playbook -i inventory.py node.yml
````

This will run against all registered nodes and ensure they are all up to date.

### Limiting a run to a specific group or node:

````bash
ansible-playbook -i inventory.py -l clinic-a node.yml
````

````bash
ansible-playbook -i inventory.py -l kenya node.yml
````

````bash
ansible-playbook -i inventory.py -l node001 node.yml
````