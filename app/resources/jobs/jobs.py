from app import app
from flask.ext.restful import Api, Resource, reqparse, abort, fields, marshal_with #filters data according to some fields
from flask import jsonify

from job_processing.queue_processor import Queue_Processor

import datetime
import json

from rq import Queue #Queue
from redis import Redis

job_post_parser = reqparse.RequestParser()
job_post_parser.add_argument('parameters', dest='parameters', type=str, required=True, help="Job Parameters")
job_post_parser.add_argument('username', dest='username', type=str, required=True, help="Username")
job_post_parser.add_argument('files', dest='files', type=str, required=True, help="Files to use")
#parameters -> workflow_id

#get workflow, get protocols, get protocol parameters, run process
class Job_queue(Resource):
	
	def post(self):
		args = job_post_parser.parse_args()
		innuendo_processor = Queue_Processor()
		jobID = innuendo_processor.insert_job(username=args.username, parameters=eval(args.parameters), files=eval(args.files))

		return {jobID:jobID}, 200

class Test(Resource):

	def get(self):
		print 'OK'
