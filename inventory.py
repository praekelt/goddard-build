##
# Required modules
##
import psycopg2
import configparser

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

	# create the cursor to query db
	cur = conn.cursor()

	# query the database
	cur.execute("""SELECT * FROM nodes""")
	rows = cur.fetchall() # fetch all the nodes

	# list of machines
	machine_objs = []

	# groups of machines
	groupings = {

		'nodes': []

	}

	# output lines for each group
	grouping_output = {

		'nodes': []

	}

	# output the row
	for row in rows:

		# get the params
		id_str 				= row[0]
		name_str 			= row[1]
		group_strs 			= row[2]
		ip_str 				= row[3]

		# create a machine object
		machine_obj = {

			'label': name_str,
			'ip': ip_str,
			'id':  int(id_str)

		}

		# append the machine
		machine_objs.append( machine_obj )

		# loop all the designated groups
		for group_str in group_strs:

			# add if not in already
			if group_str not in groupings:

				# add it
				groupings[ group_str ] = []

			# then create it
			groupings[ group_str ].append( int(id_str) )

	# loop all the machines and produce the output
	for machine_obj in machine_objs:

		# output as part 
		grouping_output['nodes'].append(' '.join([

			machine_obj['label'],
			machine_obj['ip'],

		]))

		# add each group and the label
		for group_name_str in groupings:

			# is this machine part of that group ?
			if machine_obj['id'] in groupings[ group_name_str ]:

				# check if group exists ?
				if group_name_str not in grouping_output:

					# add it
					grouping_output[ group_name_str ] = []

				# add each
				grouping_output[ group_name_str ].append( machine_obj['label'] )

	# loop and print each of the output groups
	for group_str in grouping_output.keys():

		# output the group name
		print '[' + group_str + ']'

		# loop all the machines in the group
		for line_str in grouping_output[group_str]:

			# output it
			print line_str

# run the actual logic to print out the inventory
start()

