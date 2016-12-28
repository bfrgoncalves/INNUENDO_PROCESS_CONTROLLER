from rq import Queue #Queue
from redis import Redis
import subprocess
import os
import shlex
import json

#READ CONFIG FILE
config = {}
execfile("config.py", config)

redis_conn = Redis()
q = Queue('innuendo_jobs', connection=redis_conn)

class Queue_Processor:

	def process_job(self, kwargs):
		key_value_args = []
		job_parameters = json.loads(kwargs['job_parameters'])
		########### CONTINUAR AQUI - UM JOB POR ESTIRPE ###############
		print job_parameters
		return True
		'''
		parameters = kwargs['parameters']['used Parameter']
		username = kwargs['username']

		user_folder = '/home/users/' + username + '/test'

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
			

		key_value_args.append("--spadesMaxMemory")
		key_value_args.append("4")

		print kwargs['files']
		#print key_value_args
		key_value_args = [config['INNUCA_PATH']] + key_value_args
		print key_value_args
		commands = ['sh','job_processing/launch_job.sh'] + [' '.join(key_value_args)]
		print commands
		#os.system('sh job_processing/launch_job.sh "' + ' '.join(key_value_args) + '"')
		proc = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout, stderr = proc.communicate()
		print stdout
		jobID = stdout.split(' ')
		jobID = jobID[-1].strip('\n')

		if proc.returncode == 0:
			return jobID, 200
		else:

			return '', 400
		'''

	def insert_job(self, **kwargs):
		#Insert jobs in queue
		jobID, code = self.process_job(kwargs)
		return jobID

