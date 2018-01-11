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

def submitToSLURM(user_folder, workflow_path_array, numberOfWorkflows, array_of_files, software, dependency_id, slurm_cpus):
	array_to_string = '\#'.join(workflow_path_array)

	array_tasks=[]
	count_tasks=0
	total_tasks=1

	has_dependency = False

	random_sbatch_number = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

	for a in range(0, numberOfWorkflows):
		array_tasks.append(str(count_tasks))
		count_tasks+=1
		total_tasks+=1


	#launch different template depending on the procedure (case of dependencies)
	if software == "chewBBACA":
		to_dependency = '1'
		if dependency_id != None:
			to_dependency = dependency_id
		commands = ['sh','job_processing/launch_job_chewbbaca.sh'] + [array_to_string, ','.join(array_of_files), user_folder, str(random_sbatch_number), to_dependency, slurm_cpus]
	else:
		commands = ['sh','job_processing/launch_job.sh'] + [array_to_string, ','.join(array_of_files), user_folder, str(random_sbatch_number), slurm_cpus]

	if software == "INNUca":
		has_dependency = True

	proc = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = proc.communicate()
	print stdout
	jobID = stdout.split(' ')
	jobID = jobID[-1].strip('\n')
	return jobID, array_tasks, has_dependency

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

	def process_job(self, job_parameters, current_specie, sampleName, current_user_name, current_user_id, homedir):
		key_value_args = []
		job_parameters = json.loads(job_parameters)

		count_workflows = 0
		workflow_filenames = []
		processes_ids = []
		workflows_ids = []
		outputs_names = []
		nextflow_tags = []
		dependency_id = None

		task_ids = []
		processIDs = []

		#To send to nextflow generator
		project_id = ""
		pipeline_id = ""
		nexflow_user_dir = ""

		INNUca_dependency = False

		random_pip_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)) + ".nf"


		for workflow in job_parameters:

			key_value_args = []
			count_workflows += 1;
			parameters = json.loads(workflow['parameters'])['used Parameter']
			files = json.loads(workflow['files'])
			username = workflow['username']
			strain_submitter = workflow['strain_submitter']
			workflow_name = json.loads(workflow['parameters'])['name']
			nextflow_tag = json.loads(workflow['parameters'])['Nextflow Tag']
			project_id = workflow['project_id']
			pipeline_id = workflow['pipeline_id']
			process_id = workflow['process_id']
			process_to_run = workflow['process_to_run']

			nexflow_user_dir = os.path.join(homedir,"jobs", pipeline_id)

			if not os.path.exists(nexflow_user_dir):
				os.makedirs(nexflow_user_dir)

			random_tag = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))

			nextflow_tags.append(nextflow_tag+":"+process_id)
			task_ids.append(random_tag)
			processIDs.append(process_id)

			array_of_files = []

			print process_to_run
			if not os.path.exists(os.path.join(nexflow_user_dir, "platform.config")) and process_to_run == True:
				with open(os.path.join(nexflow_user_dir, "platform.config"), "w") as nextflow_cache_file:
					nextflow_cache_file.write("process {{ ${}.cache = false}}".format(nextflow_tag))

			for x in files:
				array_of_files.append(os.path.join(strain_submitter, config['FTP_FILES_FOLDER'],files[x]))

		#RUN Nextflow GENERATOR
		nextflow_file_location = os.path.join(nexflow_user_dir, random_pip_name)
		cwd = os.getcwd()
		
		commands = ['python3', config["NEXTFLOW_GENERATOR_PATH"]] + ["-t"] + nextflow_tags + ["-o", os.path.join(nexflow_user_dir, nextflow_file_location), "--include-templates"]
		print commands
		proc = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout, stderr = proc.communicate()

		if stderr != "":
			return {'message': stderr}, 500

		#RUN NEXTFLOW
		commands = ['sh', 'job_processing/bash_scripts/nextflow_executor.sh', nexflow_user_dir, nextflow_file_location, project_id, pipeline_id, config["JOBS_ROOT_SET_OUTPUT"], sampleName, array_of_files[0], array_of_files[1], config["JOBS_ROOT_SET_REPORT"], current_user_name, current_user_id, current_specie, config["species_expected_genome_size"][current_specie], config["NEXTFLOW_PROFILE"]]
		print commands
		proc = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


		return {'task_ids':task_ids, 'process_ids': processIDs, 'subproc_id': proc.pid}, 200

	

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

	

	def insert_job(self, job_parameters, current_specie, sampleName, current_user_name, current_user_id, homedir):
		#Insert jobs in queue
		jobID, code = self.process_job(job_parameters, current_specie, sampleName, current_user_name, current_user_id, homedir)
		return jobID

	
	def download_accessions(self, download_parameters):
		#Insert jobs in queue
		output, code = self.process_download_accessions(download_parameters)
		return output
