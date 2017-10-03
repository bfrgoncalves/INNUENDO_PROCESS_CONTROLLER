from rq import Queue #Queue
from redis import Redis
import subprocess
import os
import shlex
import json
import random
import string
import random
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
	#array_of_process_ids = '\#'.join(processes_ids)
	#array_of_workflow_ids = '\#'.join(workflows_ids)
	#array_of_out_names = '\#'.join(outputs_names)
	array_tasks=[]
	count_tasks=0
	total_tasks=1

	random_sbatch_number = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

	for a in range(0, numberOfWorkflows):
		array_tasks.append(str(count_tasks))
		count_tasks+=1
		total_tasks+=1

	'''with open("job_processing/sbatch_innuca.template", "r") as template_file:
		with open("job_processing/sbatch_innuca_1.template", "w") as n_file:
			for line in template_file:
				if "#IFTRUE" in line:
					with open(workflow_path_array[0], "r") as wf_file:
						for x in wf_file:
							n_file.write(x)
				else:
					n_file.write(line)'''


	#commands = ['sh','job_processing/launch_job.sh'] + [array_to_string, ','.join(array_tasks), str(total_tasks), ','.join(array_of_files), user_folder, array_of_process_ids, array_of_workflow_ids, array_of_out_names]
	commands = ['sh','job_processing/launch_job.sh'] + [array_to_string, ','.join(array_of_files), user_folder, str(random_sbatch_number)]
	proc = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = proc.communicate()
	print stdout
	jobID = stdout.split(' ')
	jobID = jobID[-1].strip('\n')
	return jobID, array_tasks

def extract_ids(job_out):
	job_out = job_out.split('\n')
	tasks = []
	
	for x in job_out:
		if '[' in x:
			job_id = x.split('_')[0]
			task_ids = x.split('[')[1].split(']')[0].split('-')
			for k in range(int(task_ids[0]), int(task_ids[1])+1):
				tasks.append(job_id + '_' + str(k))
		elif x != '':
			tasks.append(x)
	
	return tasks


class Queue_Processor:

	def process_job(self, job_parameters, current_specie, sampleName, current_user_name, current_user_id):
		key_value_args = []
		job_parameters = json.loads(job_parameters)

		count_workflows = 0;
		workflow_filenames = [];
		processes_ids = [];
		workflows_ids = [];
		outputs_names = [];

		'''workflow_job_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
		workflow_filepath = os.path.join(config['JOBS_FOLDER'], job_parameters[0]["username"] + '_' + workflow_job_name +'.txt')
		workflow_filenames.append(workflow_filepath)'''



		for workflow in job_parameters:

			key_value_args = []
			count_workflows += 1;
			parameters = json.loads(workflow['parameters'])['used Parameter']
			files = json.loads(workflow['files'])
			username = workflow['username']
			strain_submitter = workflow['strain_submitter']
			workflow_name = json.loads(workflow['parameters'])['name']

			array_of_files = []

			print strain_submitter
			user_folder = '/home/users/' + username
			submitter_folder = '/home/users/' + strain_submitter

			for x in files:
				array_of_files.append(os.path.join(submitter_folder, config['FTP_FILES_FOLDER'],files[x]))

			workflow_job_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
			workflow_filepath = os.path.join(config['JOBS_FOLDER'], username + '_' + workflow_job_name +'.sh')
			

			key_value_args, prev_application_steps, after_application_steps, status_definition = process_parameters(parameters, user_folder, workflow, current_specie, workflow_name, sampleName, current_user_name, current_user_id)
			key_value_args, softwarePath, language = setFilesByProgram(key_value_args, workflow)

			#TEST SUBMIT ONLY ONE SBATCH PER PROCEDURE
			workflow_filenames = []

			if key_value_args != False:
				key_value_args = [language, softwarePath] + key_value_args
				with open(workflow_filepath, 'a') as jobs_file:
					jobs_file.write(prev_application_steps.replace("STEPID", str(count_workflows)).replace("SLURM_ARRAY_JOB_ID", "$1"))
					jobs_file.write(' '.join(key_value_args).replace("STEPID", str(count_workflows)).replace("SLURM_ARRAY_JOB_ID", "$1"))
					jobs_file.write(after_application_steps.replace("STEPID", str(count_workflows)).replace("SLURM_ARRAY_JOB_ID", "$1"))
					jobs_file.write(status_definition.replace("STEPIDMINUS1", str(count_workflows-1)).replace("STEPID", str(count_workflows)).replace("SLURM_ARRAY_JOB_ID", "$1"))
				workflow_filenames.append(workflow_filepath)
				'''processes_ids.append(process_ids)
				workflows_ids.append(workflow_id)
				outputs_names.append(output_name)'''
				jobID, task_numbers = submitToSLURM(user_folder, workflow_filenames, count_workflows, array_of_files)

		#jobID, task_numbers = submitToSLURM(user_folder, workflow_filenames, count_workflows, array_of_files)

		#check job ids via squeue
		#commands = 'squeue --job '+ jobID +' | sed "1d" | sed "s/ \+/\t/g" | cut -f2'
		#print commands.split(' ')
		'''commands = 'sh job_processing/get_number_of_jobs.sh ' + jobID
		proc1 = subprocess.Popen(commands.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout, stderr = proc1.communicate()'''

		task_ids = []

		for t in task_numbers:
			task_ids.append(jobID + "_" + t)

		'''if stderr == '':
			task_ids = extract_ids(stdout)'''

		return {'task_ids':task_ids}, 200

	

	def process_download_accessions(self, download_parameters):

		user_folder = '/home/users/' + download_parameters.username + '/' + config["FTP_FILES_FOLDER"]
		ena_file_txt = os.path.join(user_folder, 'ENA_file.txt')

		output_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
		
		with open(ena_file_txt, 'w') as ena_file:
			ena_file.write('\n'.join(download_parameters.accession_numbers.split(",")) + '\n')
		
		f = open(os.path.join(user_folder, output_id + '_download.txt'), "w")

		#GETSEQ ENA PASSING FILES TO PREVIOUS DIR
		commands = 'python dependencies/getSeqENA/getSeqENA.py -l ' + ena_file_txt + ' -o ' + user_folder
		proc1 = subprocess.Popen(commands.split(' '), stdout=f)


		#stdout, stderr = proc1.communicate()

		return {'output_file_id': output_id + '_download.txt'}, 200

	

	def insert_job(self, job_parameters, current_specie, sampleName, current_user_name, current_user_id):
		#Insert jobs in queue
		jobID, code = self.process_job(job_parameters, current_specie, sampleName, current_user_name, current_user_id)
		return jobID

	
	def download_accessions(self, download_parameters):
		#Insert jobs in queue
		output, code = self.process_download_accessions(download_parameters)
		return output
