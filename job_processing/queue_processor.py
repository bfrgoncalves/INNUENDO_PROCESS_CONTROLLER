from rq import Queue #Queue
from redis import Redis
import subprocess
import os
import shlex
import json
import random
import string
from process_parameters import process_parameters

#READ CONFIG FILE
config = {}
execfile("config.py", config)

redis_conn = Redis()
q = Queue('innuendo_jobs', connection=redis_conn)

def setFilesByProgram(key_value_args, workflow):
	#print workflow
	wf_params = json.loads(workflow['parameters'])
	if wf_params['used Software'] in config['APPLICATIONS_ARRAY']:
		software = wf_params['used Software']
		if software == '':
			software = 'INNUca'
		softwarePath = config['FILETYPES_SOFTWARE'][software][0]['path']
		language = config['FILETYPES_SOFTWARE'][software][0]['language']
		return key_value_args, softwarePath, language
	else:
		return False, False

def submitToSLURM(user_folder, workflow_path_array, numberOfWorkflows):
	array_to_string = '\#'.join(workflow_path_array)
	array_tasks=[]
	count_tasks=0
	for a in range(0, numberOfWorkflows):
		array_tasks.append(str(count_tasks))
		count_tasks+=1
	print array_to_string
	print array_tasks
	commands = ['sh','job_processing/launch_job.sh'] + [array_to_string, ','.join(array_tasks)]
	proc = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = proc.communicate()
	print stdout
	jobID = stdout.split(' ')
	jobID = jobID[-1].strip('\n')
	return jobID

class Queue_Processor:

	def process_job(self, job_parameters):
		key_value_args = []
		job_parameters = json.loads(job_parameters)

		print job_parameters

		count_workflows = 0;
		workflow_filenames = [];
		for workflow in job_parameters:

			key_value_args = []
			count_workflows += 1;
			parameters = json.loads(workflow['parameters'])['used Parameter']
			username = workflow['username']
			print parameters

			workflow_job_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
			workflow_filepath = os.path.join(config['JOBS_FOLDER'], username + '_' + workflow_job_name +'.txt')
			
			user_folder = '/home/users/' + username

			key_value_args = process_parameters(parameters, user_folder)
			key_value_args, softwarePath, language = setFilesByProgram(key_value_args, workflow)

			if key_value_args != False:
				key_value_args = [language, softwarePath] + key_value_args
				with open(workflow_filepath, 'w') as jobs_file:
					jobs_file.write(' '.join(key_value_args))
				workflow_filenames.append(workflow_filepath)

		jobID = submitToSLURM(user_folder, workflow_filenames, count_workflows)


		return jobID, 200


	def insert_job(self, job_parameters):
		#Insert jobs in queue
		jobID, code = self.process_job(job_parameters)
		return jobID
