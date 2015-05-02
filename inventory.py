#!/usr/bin/python
##
# Required modules
##
import psycopg2
import psycopg2.extras
import configparser
import json
import sys
import os

# starting point if the script is run
def start():

	# read in our config
	config = configparser.ConfigParser()
	config.read('goddard-ansible.ini')

	# read config variables
	config_database_name_str 	= config['database']['name']
	config_database_user_str 	= config['database']['user']
	config_database_pwd_str 	= config['database']['password']
	config_database_host_str 	= config['database']['host']

	# connect to the database
	try:
		conn = psycopg2.connect("dbname='" + config_database_name_str + "' user='" + config_database_user_str + "' host='" + config_database_host_str + "' password='" + config_database_pwd_str + "'")
	except Exception, e:
		print "Problems connecting to the database"
		print e
		sys.exit(1)

	# create the cursor to query db
	cur = conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
	cur.execute("""SELECT * FROM apps""")
	app_objs = cur.fetchall() # fetch all the nodes

	nodecur = conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
	nodecur.execute("""SELECT * FROM nodes""")
	node_objs = nodecur.fetchall() # fetch all the nodes

	groupcur = conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
	groupcur.execute("""SELECT * FROM groups""")
	group_objs = groupcur.fetchall() # fetch all the groups

	installcur = conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
	installcur.execute("""SELECT * FROM installs""")
	install_objs = installcur.fetchall() # fetch all the groups

	# list of machines
	machine_objs = []

	# groups of machines
	groupings = {

		'nodes': []

	}

	# output lines for each group
	grouping_output = {

		'nodes': [],
		'_meta': {

			'hostvars': {}

		}

	}

	# loop them all
	for node_obj in node_objs:

		# get the params
		node_id_str = node_obj.id
		node_serial_str = node_obj.serial
		node_label_str = node_obj.name
		node_port_str  = node_obj.port
		node_management_port_str = node_obj.mport
		node_group_id = node_obj.groupId

		# create a machine object
		machine_obj = {

			'label': node_label_str,
			'ip': 'localhost',
			'id':  int(node_id_str),
			'meta': {},
			'serial': node_serial_str

		}

		# add ip to meta
		machine_obj['meta'] = {

			'ansible_ssh_user': 'goddard',
			'ansible_sudo': True,
			'ansible_sudo_pass': 'rogerwilco',
			'ansible_ssh_pass': 'rogerwilco',
			'ansible_ssh_host': 'localhost',
			'ansible_ssh_port': int(node_port_str),
			'apps': [
			]

		}

		# keep track of app keys
		app_key_strs = []

		# add in the extra details
		machine_obj['meta']['node'] = {

			'id': node_id_str,
			'serial': node_serial_str,
			'label': node_label_str

		}

		# add to general group output as part 
		grouping_output['nodes'].append(node_serial_str)

		# if this node belongs to a group ...
		if node_group_id != None:

			# loop them all
			for app_obj in app_objs:

				# group details
				app_id_str = app_obj.id
				app_name_str = app_obj.name
				app_key_str = app_obj.key
				app_visible_str = app_obj.visible
				app_portal_str = app_obj.portal

				# loop all the installs for this nodes' groups
				for install_obj in install_objs:

					# and ... ?
					if int(install_obj.groupId) == int(node_group_id):

						# add if not in already
						if app_key_str not in grouping_output:

							# add it
							grouping_output[ app_key_str ] = []

						# add the serial if not in group
						if node_serial_str not in grouping_output[ app_key_str ]:							

							# then create it
							grouping_output[ app_key_str ].append( node_serial_str )

						# generate the domain
						domain_str = app_key_str + '.goddard.com'

						# check if this is a portal or not
						if app_portal_str == True:
							domain_str = 'goddard.com'

						# add the key
						if app_key_str not in app_key_strs: 

							#add it
							app_key_strs.append(app_key_str)

							# append to the apps
							machine_obj['meta']['apps'].append({

								'id': app_id_str,
								'port': 6100 + int(app_id_str),
								'name': app_name_str,
								'description': app_obj.description,
								'logo': '',
								'key': app_key_str,
								'domain': domain_str,
								'internal': app_visible_str == False

							})

			# loop them all
			for group_obj in group_objs:

				# group details
				group_id_str = group_obj.id
				group_name_str = group_obj.name
				group_key_str = group_obj.key
				group_description_str = group_obj.description
				group_slug_str = group_obj.name

				# and ... ?
				if int(group_id_str) == int(node_group_id):

					# add group details
					machine_obj['meta']['group'] = {

						'id': group_id_str,
						'name': group_name_str,
						'description': group_description_str,
						'slug': group_slug_str

					}

					# add if not in already
					if group_key_str not in grouping_output:

						# add it
						grouping_output[ group_key_str ] = []

					# then create it
					grouping_output[ group_key_str ].append( node_serial_str )

		# add the meta
		grouping_output['_meta']['hostvars'][ node_serial_str ] = machine_obj['meta']

	print json.dumps(grouping_output)

# run the actual logic to print out the inventory
start()

