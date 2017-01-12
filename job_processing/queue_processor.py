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
		softwarePath = config['FILETYPES_SOFTWARE'][software][0]['path']
		language = config['FILETYPES_SOFTWARE'][software][0]['language']
		return key_value_args, softwarePath, language
	else:
		return False, False

def submitToSLURM(user_folder, workflow_path_array, numberOfWorkflows, array_of_files):
	array_to_string = '\#'.join(workflow_path_array)
	array_tasks=[]
	count_tasks=0
	for a in range(0, numberOfWorkflows):
		array_tasks.append(str(count_tasks))
		count_tasks+=1
	print array_to_string
	print array_tasks

	commands = ['sh','job_processing/launch_job.sh'] + [array_to_string, ','.join(array_tasks), ','.join(array_of_files), user_folder]
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
			files = json.loads(workflow['files'])
			username = workflow['username']

			array_of_files = []

			for x in files:
				array_of_files.append(files[x])

			workflow_job_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
			workflow_filepath = os.path.join(config['JOBS_FOLDER'], username + '_' + workflow_job_name +'.txt')
			
			user_folder = '/home/users/' + username

			key_value_args, prev_application_steps, after_application_steps = process_parameters(parameters, user_folder, workflow)
			key_value_args, softwarePath, language = setFilesByProgram(key_value_args, workflow)

			if key_value_args != False:
				key_value_args = [language, softwarePath] + key_value_args
				with open(workflow_filepath, 'w') as jobs_file:
					jobs_file.write(prev_application_steps)
					jobs_file.write(' '.join(key_value_args))
					jobs_file.write(after_application_steps)
				workflow_filenames.append(workflow_filepath)

		jobID = submitToSLURM(user_folder, workflow_filenames, count_workflows, array_of_files)

		#check job ids via squeue
		#commands = 'squeue --job '+ jobID +' | sed "1d" | sed "s/ \+/\t/g" | cut -f2'
		#print commands.split(' ')
		commands = 'squeue --job '+ jobID
		proc1 = subprocess.Popen(commands.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		#print proc1.communicate()
		commands = "sed '1d'"
		proc2 = subprocess.Popen(commands.split(' '), stdin=proc1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		commands = 'sed "s/ \+/\t/g"'
		print 'P2', proc2.communicate()
		proc3 = subprocess.Popen(commands.split(' '), stdin=proc2.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		commands = 'cut -f2'
		print 'P3', proc3.communicate()
		proc4 = subprocess.Popen(commands.split(' '), stdin=proc3.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		print 'P4', proc4.communicate()
		stdout, stderr = proc4.communicate()
		#print stdout, stderr


		return jobID, 200


	def insert_job(self, job_parameters):
		#Insert jobs in queue
		jobID, code = self.process_job(job_parameters)
		return jobID
