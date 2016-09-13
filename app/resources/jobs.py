from app import app
from flask.ext.restful import Api, Resource, reqparse, abort, fields, marshal_with #filters data according to some fields
from flask import jsonify
from flask.ext.security import current_user, login_required

#Defining post arguments parser
job_post_parser = reqparse.RequestParser()
#job_post_parser.add_argument('', dest='name', type=str, required=True, help="Workflow name")
#job_post_parser.add_argument('steps', dest='steps', type=str, required=True, help="Protocol steps")

#Defining JOBS Resources

class JobsResource(Resource):

	def get(self):
		return { "jobs": "All jobs resource" }

	def post(self):
		return { "status": "Posted" }

class JobResource(Resource):

	def get(self, id):
		return { "job": "Job resource" }

class JobStatusResource(Resource):

	def get(self, id):
		return { "status": "Job status resource" }
