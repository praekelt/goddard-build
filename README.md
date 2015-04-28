# Goddard Build

## About

Takes care of "building" (provisioning) the nodes. The Hub server connects over SSH and makes use of http://www.ansible.com.

The playbook only touches application specific services to make sure the node is always connected.

The script does a few steps:

For Hub & Nodes:

* Updates hostname
* Updates to correct timezone (*SAST*)
* Updates the package list
* Safe Upgrades all the security updates
* Installs needed debs/tools

For Nodes: 

* Installs and configures Docker
* Adds all the rquired images to Docker
* Installs and configures NGINX for docker and local pages
* Adds local data files that allow the Node to read it's own installed apps

For Hub:

* Pulls down code for the Hub Server
* Sets up NGINX for the Hub
* Sets up the Upstart service to run the Node
* Restarts all the touched services to ensure they are running

## Running

The inventory of all the nodes is pulled from a database table. This table contains all the configured nodes and their details.

### To run:

#### Hub Server

The hub server requires a quick inventory file that points to the existing servers that you wish to run the playbook against:

````bash
ansible-playbook -i {some-inventory} hub.yml

#### Nodes

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