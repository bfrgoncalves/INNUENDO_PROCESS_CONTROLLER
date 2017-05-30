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

job_get_parser = reqparse.RequestParser()
job_get_parser.add_argument('job_id', dest='job_id', type=str, required=True, help="Job ID")
job_get_parser.add_argument('project_id', dest='project_id', type=str, required=True, help="project_id ID")
job_get_parser.add_argument('pipeline_id', dest='pipeline_id', type=str, required=True, help="pipeline_id ID")
job_get_parser.add_argument('process_id', dest='process_id', type=str, required=True, help="process_id ID")
job_get_parser.add_argument('username', dest='username', type=str, required=True, help="Username")
#job_post_parser.add_argument('username', dest='username', type=str, required=True, help="Username")
#job_post_parser.add_argument('files', dest='files', type=str, required=True, help="Files to use")
#parameters -> workflow_id

file_get_parser = reqparse.RequestParser()
file_get_parser.add_argument('username', dest='username', type=str, required=True, help="Username")

download_file_get_parser = reqparse.RequestParser()
download_file_get_parser.add_argument('username', dest='username', type=str, required=True, help="Username")
download_file_get_parser.add_argument('accession_numbers', dest='accession_numbers', type=str, required=True, help="Accession numbers")

#get workflow, get protocols, get protocol parameters, run process

#READ CONFIG FILE
config = {}
execfile("config.py", config)

def load_results_from_file(job_id, username):

	user_folder = '/home/users/' + username + '/' + job_id.split('_')[0] + '/*_' + job_id + '/*.*'

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

	for i in onlyfiles:
		data = open(i).read()
		print i
		try:
			json_data = json.loads(data)
		except ValueError:
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
		print job_parameters
		innuendo_processor = Queue_Processor()
		jobID = innuendo_processor.insert_job(job_parameters=job_parameters)

		return {'jobID':jobID}, 200

	def get(self):

		args = job_get_parser.parse_args()
		job_id = args.job_id
		print "JOB", job_id
		commands = 'sh job_processing/get_job_status.sh ' + job_id.split("_")[0]
		proc1 = subprocess.Popen(commands.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout, stderr = proc1.communicate()
		print "STDOUT", stdout, len(stdout.split('\t'))

		results = [[],[]]
		store_in_db = False


		if len(stdout.split('\t')) == 1:
			commands = 'python job_processing/get_program_input.py --project ' + args.project_id + ' --pipeline ' + args.pipeline_id + ' --process ' + args.process_id + ' -t status'
			#commands = 'sh job_processing/get_completed_jobs.sh ' + job_id.split('_')[0]
			proc1 = subprocess.Popen(commands.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			stdout, stderr = proc1.communicate()
			#parts = stdout.split('\t')

			stdout = job_id + '\t' + stdout

			print stdout

			if stdout == "COMPLETED":
				print "COMPLETED"
				results = load_results_from_file(job_id, args.username)
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
		files_folder = os.path.join('/home/users/', args.username, config['FTP_FILES_FOLDER'], '*.gz')
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
		with open(file_folder, 'r') as file_to_send:
			for line in file_to_send:
				file_array.append(line)
		
		return {'output':file_array}, 200



