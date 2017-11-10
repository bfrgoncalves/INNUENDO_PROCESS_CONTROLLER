from app import app
from flask.ext.restful import Api, Resource, reqparse, abort, fields, marshal_with #filters data according to some fields
from flask import jsonify

from job_processing.queue_processor import Queue_Processor

import datetime
import json
import subprocess
import os
from os import listdir
from os.path import isfile, join

from rq import Queue #Queue
from redis import Redis

import glob

job_post_parser = reqparse.RequestParser()
job_post_parser.add_argument('data', dest='data', type=str, required=True, help="Job Parameters")
job_post_parser.add_argument('current_specie', dest='current_specie', type=str, required=True, help="Current Specie")
job_post_parser.add_argument('sampleName', dest='sampleName', type=str, required=True, help="Sample Name")
job_post_parser.add_argument('current_user_name', dest='current_user_name', type=str, required=True, help="Current user name")
job_post_parser.add_argument('current_user_id', dest='current_user_id', type=str, required=True, help="current user id")
job_post_parser.add_argument('homedir', dest='homedir', type=str, required=True, help="home dir")

job_get_parser = reqparse.RequestParser()
job_get_parser.add_argument('job_id', dest='job_id', type=str, required=True, help="Job ID")
job_get_parser.add_argument('project_id', dest='project_id', type=str, required=True, help="project_id ID")
job_get_parser.add_argument('pipeline_id', dest='pipeline_id', type=str, required=True, help="pipeline_id ID")
job_get_parser.add_argument('process_id', dest='process_id', type=str, required=True, help="process_id ID")
job_get_parser.add_argument('username', dest='username', type=str, required=True, help="Username")
job_get_parser.add_argument('homedir', dest='homedir', type=str, required=True, help="Home dir")
job_get_parser.add_argument('from_process_controller', dest='from_process_controller', type=str, required=True, help="from_process_controller")
#job_post_parser.add_argument('username', dest='username', type=str, required=True, help="Username")
#job_post_parser.add_argument('files', dest='files', type=str, required=True, help="Files to use")
#parameters -> workflow_id

file_get_parser = reqparse.RequestParser()
file_get_parser.add_argument('username', dest='username', type=str, required=True, help="Username")
file_get_parser.add_argument('homedir', dest='homedir', type=str, required=True, help="Home dir")

download_file_get_parser = reqparse.RequestParser()
download_file_get_parser.add_argument('username', dest='username', type=str, required=True, help="Username")
download_file_get_parser.add_argument('accession_numbers', dest='accession_numbers', type=str, required=True, help="Accession numbers")

copy_schema_get_parser = reqparse.RequestParser()
copy_schema_get_parser.add_argument('schema_to_copy', dest='schema_to_copy', type=str, required=True, help="chewBBACA schema to copy")

#get workflow, get protocols, get protocol parameters, run process

#READ CONFIG FILE
config = {}
execfile("config.py", config)

def load_results_from_file(job_id, homedir):
	print homedir
	user_folder = os.path.join(homedir, job_id.split('_')[0] + '/*_' + job_id.split('_')[0] + "_" + str(int(job_id.split('_')[1]) + 1) + '/*.*')
	print user_folder

	onlyfiles = [f for f in glob.glob(user_folder)]

	'''for i in onlyfiles:
		if 'chewBBACA' in i:
			user_folder += '/*'
			break

		elif 'INNUca' in i:
			user_folder += '/*'
			break'''

	onlyfiles = [f for f in glob.glob(user_folder)]

	results = {}

	array_of_results = {}
	array_of_paths = {}
	
	print onlyfiles
	print "##################################################"

	for i in onlyfiles:
		try:
			data = open(i).read()
			json_data = json.loads(data)
		except Exception:
			if "PathoTyping" in i or "Pathotyping" in i:
				try:
					json_data = {}
					json_data["result"] = data
				except Exception:
					json_data = {"stats": "Not JSON"}
			else:
				json_data = {"stats": "Not JSON"}

		if "run_output" in i:
			array_of_results["run_output"] = json_data;
			array_of_paths["run_output"] = i;
		elif "run_stats" in i:
			array_of_results["run_stats"] = json_data;
			array_of_paths["run_stats"] = i;
		elif "run_info" in i:
			array_of_results["run_info"] = json_data;
			array_of_paths["run_info"] = i;
	
	return [array_of_results, array_of_paths]


class Job_queue(Resource):
	
	def post(self):
		args = job_post_parser.parse_args()
		job_parameters = args.data
		current_specie = args.current_specie
		sampleName = args.sampleName
		current_user_name = args.current_user_name
		current_user_id = args.current_user_id

		innuendo_processor = Queue_Processor()
		jobID = innuendo_processor.insert_job(job_parameters=job_parameters, current_specie=current_specie, sampleName=sampleName, current_user_name=current_user_name, current_user_id=current_user_id, homedir=args.homedir)

		return {'jobID':jobID}, 200

	def get(self):

		args = job_get_parser.parse_args()
		job_id = args.job_id
		from_process_controller = args.from_process_controller
		print "JOB", job_id
		commands = 'sh job_processing/get_job_status.sh ' + job_id.split("_")[0]
		proc1 = subprocess.Popen(commands.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout, stderr = proc1.communicate()
		print "STDOUT", stdout, len(stdout.split('\t'))
		go_to_pending = False

		results = [[],[]]
		store_in_db = False

		if len(stdout.split('\t')) == 2 and from_process_controller != 'true':
			print stdout.split('\t')[0]
			if stdout.split('\t')[0].replace(".","_") == job_id:
				stdout = job_id + '\tR'
			else:
				go_to_pending = True


		if len(stdout.split('\t')) == 1 or go_to_pending == True or from_process_controller == 'true':
			print go_to_pending
			print '--project ' + args.project_id + ' --pipeline ' + args.pipeline_id + ' --process ' + args.process_id + ' -t status'
			commands = 'python job_processing/get_program_input.py --project ' + args.project_id + ' --pipeline ' + args.pipeline_id + ' --process ' + args.process_id + ' -t status'
			#commands = 'sh job_processing/get_completed_jobs.sh ' + job_id.split('_')[0]
			proc1 = subprocess.Popen(commands.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			stdout, stderr = proc1.communicate()
			#parts = stdout.split('\t')
			print stdout, stderr

			stdout = job_id + '\t' + stdout

			print stdout

			if "COMPLETED" in stdout or "WARNING" in stdout or "FAILED" in stdout:
				print "COMPLETED"
				results = load_results_from_file(job_id, args.homedir)
				if len(results[1].keys()) == 0:
					store_in_db = False
				else:
					store_in_db = True

			'''if len(parts) == 0:
				stdout = job_id + '\tFAILED'
			else:
				results = load_results_from_file(job_id, args.username)
				store_in_db = True'''

		return {'stdout':stdout, 'store_in_db':store_in_db, 'results':results[0], 'paths':results[1], 'job_id': job_id}


class FilesResource(Resource):

	def get(self):

		args = file_get_parser.parse_args()
		files_folder = os.path.join(args.homedir, config['FTP_FILES_FOLDER'], '*.gz')
		v_files = []
		for fl in glob.glob(files_folder):
		    #print os.path.basename(fl)
		    v_files.append(os.path.basename(fl))
		
		return {'files': sorted(v_files)}, 200


class DownloadFilesResource(Resource):

	def post(self):
		args = download_file_get_parser.parse_args()
		innuendo_processor = Queue_Processor()
		output = innuendo_processor.download_accessions(download_parameters=args)
		print "OUTPUT", output
		return output, 200

	def get(self):
		args = download_file_get_parser.parse_args()
		file_array = []
		file_folder = os.path.join('/home/users/', args.username, config['FTP_FILES_FOLDER'], args.accession_numbers)
		print file_folder
		with open(file_folder, 'r') as file_to_send:
			for line in file_to_send:
				file_array.append(line)
		
		return {'output':file_array}, 200


class CopyChewSchema(Resource):

	def get(self):
		args = copy_schema_get_parser.parse_args()
		cwd = os.getcwd()
		print cwd
		commands = ['cp', '-r', './dependencies/chewBBACA/chewBBACA_schemas_on_compute/'+args.schema_to_copy, './dependencies/chewBBACA/chewBBACA_schemas/'+args.schema_to_copy+'_new']
		print commands
		proc = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout, stderr = proc.communicate()
		commands = ['rm','-rf', './dependencies/chewBBACA/chewBBACA_schemas/'+args.schema_to_copy]
		print commands
		proc = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout, stderr = proc.communicate()
		commands = ['mv','./dependencies/chewBBACA/chewBBACA_schemas/'+args.schema_to_copy+'_new', './dependencies/chewBBACA/chewBBACA_schemas/'+args.schema_to_copy]
		print commands
		proc = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout, stderr = proc.communicate()
		return 200



