#!bin/python
##
# Required modules
##
import psycopg2
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
	cur = conn.cursor()

	# query the database
	cur.execute("""SELECT * FROM apps""")
	app_objs = cur.fetchall() # fetch all the nodes

	nodecur = conn.cursor()
	nodecur.execute("""SELECT * FROM nodes""")
	node_objs = nodecur.fetchall() # fetch all the nodes

	groupcur = conn.cursor()
	groupcur.execute("""SELECT * FROM groups""")
	group_objs = groupcur.fetchall() # fetch all the groups

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

	# output the row
	for app_obj in app_objs:

		# get the params
		id_str = app_obj[0]
		name_str = app_obj[1]
		image_str = app_obj[2]
		description_str = app_obj[3]
		slug_str = app_obj[4]

		# add the group
		# add if not in already
		if slug_str not in groupings:

			# add it
			groupings[ slug_str ] = []

		# loop them all
		for node_obj in node_objs:

			# get the params
			node_id_str = node_obj[0]
			node_serial_str = node_obj[1]
			node_label_str = node_obj[21]
			node_port_str  = node_obj[10]
			node_management_port_str = node_obj[11]

			# create a machine object
			machine_obj = {

				'label': node_label_str,
				'ip': 'localhost',
				'id':  int(node_id_str),
				'meta': {},
				'serial': node_serial_str

			}

			# add ip to meta
			machine_obj['meta']['ansible_ssh_host'] = machine_obj['ip']

			# add the meta
			grouping_output['_meta']['hostvars'][ machine_obj['label'] ] = machine_obj['meta']

			# add to general group
			# output as part 
			grouping_output['nodes'].append(' '.join([

				node_label_str,
				'ansible_ssh_host=' + machine_obj['ip'],
				'ansible_ssh_port=' + str(node_port_str)

			]))

			# loop them all
			for group_obj in group_objs:

				# group details
				group_id_str = group_obj[0]
				group_name_str = group_obj[1]
				group_slug_str = group_obj[2]

				# set the name
				group_full_name_str = group_slug_str + ':children'

				# add if not in already
				if group_slug_str not in groupings:

					# add it
					groupings[ group_slug_str ] = []

				# then create it
				groupings[ group_slug_str ].append( node_label_str )

	print json.dumps(grouping_output)

# run the actual logic to print out the inventory
start()

