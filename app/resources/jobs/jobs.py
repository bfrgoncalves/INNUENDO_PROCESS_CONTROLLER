from app import app
from flask.ext.restful import Api, Resource, reqparse, abort, fields, marshal_with #filters data according to some fields
from flask import jsonify

from job_processing.queue_processor import Queue_Processor

import datetime
import json

from rq import Queue #Queue
from redis import Redis

job_post_parser = reqparse.RequestParser()
job_post_parser.add_argument('data', dest='data', type=str, required=True, help="Job Parameters")

job_get_parser = reqparse.RequestParser()
job_get_parser.add_argument('job_id', dest='job_id', type=str, required=True, help="Job ID")
#job_post_parser.add_argument('username', dest='username', type=str, required=True, help="Username")
#job_post_parser.add_argument('files', dest='files', type=str, required=True, help="Files to use")
#parameters -> workflow_id

#get workflow, get protocols, get protocol parameters, run process
class Job_queue(Resource):
	
	def post(self):
		args = job_post_parser.parse_args()
		job_parameters = args.data
		innuendo_processor = Queue_Processor()
		jobID = innuendo_processor.insert_job(job_parameters=job_parameters)

		return {'jobID':jobID}, 200

	def get(self):

		args = job_post_parser.parse_args()
		job_id = args.job_id
		commands = 'sh job_processing/get_job_status.sh ' + job_id
		proc1 = subprocess.Popen(commands.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout, stderr = proc1.communicate()
		print stdout, stderr
		print 'OK'

		return stdout
