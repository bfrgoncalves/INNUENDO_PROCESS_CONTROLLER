
def process_parameters(parameters, user_folder):

	key_value_args = []

	for key, value in parameters.iteritems():
		key_value_args.append(str(key))

		if str(key) == '-i':
			#value += kwargs['username']
			key_value_args.append(str(user_folder))
			key_value_args.append('-o')
			key_value_args.append(str(user_folder))
		
		elif len(value.split(' ')) > 1:
			key_value_args.append("'" + str(value) + "'")
		else:
			key_value_args.append(str(value))

	return key_value_args