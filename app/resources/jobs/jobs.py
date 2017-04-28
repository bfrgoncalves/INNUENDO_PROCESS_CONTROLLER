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

	array_of_results = []
	array_of_paths = []

	for i in onlyfiles:
		data = open(i).read()
		print i
		try:
			json_data = json.loads(data)
		except ValueError:
			json_data = {"stats": "Not JSON"}

		array_of_results.append(json_data)
		array_of_paths.append(i)

	
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
		commands = 'sh job_processing/get_job_status.sh ' + job_id
		proc1 = subprocess.Popen(commands.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout, stderr = proc1.communicate()
		print stdout, len(stdout.split('\t'))

		results = [[],[]]
		store_in_db = False


		if len(stdout.split('\t')) == 1:
			commands = 'sh job_processing/get_completed_jobs.sh ' + job_id.split('_')[0]
			proc1 = subprocess.Popen(commands.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			stdout, stderr = proc1.communicate()
			parts = stdout.split('\t')
			if len(parts) == 0:
				stdout = job_id + '\tFAILED'
			else:
				results = load_results_from_file(job_id, args.username)
				store_in_db = True

		return {'stdout':stdout, 'store_in_db':store_in_db, 'results':results[0], 'paths':results[1]}


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

	def get(self):
		args = download_file_get_parser.parse_args()
		user_folder = '/home/users/' + args.username + '/' + config["FTP_FILES_FOLDER"]
		print user_folder
		ena_file_txt = os.path.join(user_folder, 'ENA_file.txt')
		with open(ena_file_txt, 'w') as ena_file:
			ena_file.write('\n'.join(args.accession_numbers.split(",")) + '\n')
		
		print ena_file_txt
		commands = 'python dependencies/getSeqENA/getSeqENA.py -l ' + ena_file_txt + ' -o ' + user_folder
		proc1 = subprocess.Popen(commands.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout, stderr = proc1.communicate()
		print stdout, stderr

		numbers = args.accession_numbers.split(",")

		for number in numbers:
			if number != "":
				commands = 'mv ' + os.path.join(user_folder, number, number) + '* ' + user_folder + ' ;'
				commands += 'rm -r ' + os.path.join(user_folder, number) + ' ;'
				os.system(commands)

		return 200



