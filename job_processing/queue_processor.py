from rq import Queue #Queue
from redis import Redis
import subprocess
import os
import shlex
import json
import random
import string

#READ CONFIG FILE
config = {}
execfile("config.py", config)

redis_conn = Redis()
q = Queue('innuendo_jobs', connection=redis_conn)

def setFilesByProgram(key_value_args, workflow):

	workflow = json.loads()
	if workflow['used Parameter']['usedSoftware'] in config['APPLICATIONS_ARRAY']:
		software = workflow['used Parameter']['usedSoftware']
		software = 'INNUca'
		softwarePath = config['FILETYPES_SOFTWARE'][software]['path']
		language = config['FILETYPES_SOFTWARE'][software]['language']
		return key_value_args, softwarePath, language
	else:
		return False, False

def submitToSLURM(workflow_path_array, numberOfWorkflows):
	array_to_string = '#'.join(workflow_path_array)
	print array_to_string
	commands = ['sh','job_processing/launch_job.sh'] + [array_to_string, numberOfWorkflows]
	proc = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = proc.communicate()
	print stdout

class Queue_Processor:

	def process_job(self, job_parameters):
		key_value_args = []
		job_parameters = json.loads(job_parameters)
		########### CONTINUAR AQUI - UM JOB POR ESTIRPE ###############
		print job_parameters

		count_workflows = 0;
		workflow_filenames = [];
		for workflow in job_parameters:

			count_workflows += 1;
			print workflow
			parameters = json.loads(workflow['parameters'])['used Parameter']
			#parameters = parameters['used Parameter']
			print parameters
			username = workflow['username']

			workflow_job_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
			workflow_filepath = os.path.join(config['JOBS_FOLDER'], username + '_' + workflow_job_name +'.txt')
			
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

			key_value_args, softwarePath, language = setFilesByProgram(key_value_args, workflow)

			if key_value_args != False:
				key_value_args = [language, softwarePath] + key_value_args
				print key_value_args
				#commands = ['sh','job_processing/launch_job.sh'] + [' '.join(key_value_args)]
				with os.open(workflow_filepath) as jobs_file:
					jobs_file.write(' '.join(key_value_args))
				print commands
				workflow_filenames.append(workflow_filepath)
				#os.system('sh job_processing/launch_job.sh "' + ' '.join(key_value_args) + '"')
				
				#proc = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				#stdout, stderr = proc.communicate()
				#print stdout
				#jobID = stdout.split(' ')
				#jobID = jobID[-1].strip('\n')

		submitToSLURM(workflow_filenames, count_workflows-1)

		#commands = ['sh','job_processing/launch_job.sh'] + [' '.join(key_value_args)]


		return 1,200

		#key_value_args.append("--spadesMaxMemory")
		#key_value_args.append("4")

		#if proc.returncode == 0:
		#	return jobID, 200
		#else:
		#	return '', 400

	def insert_job(self, job_parameters):
		#Insert jobs in queue
		jobID, code = self.process_job(job_parameters)
		return jobID
