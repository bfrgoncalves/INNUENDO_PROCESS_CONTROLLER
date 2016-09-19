from app import app, db
from flask.ext.restful import Api, Resource, reqparse, abort, fields, marshal_with #filters data according to some fields
from flask import jsonify

from flask.ext.security import current_user, login_required, roles_required
import datetime
import subprocess
import os
from config import ROOT_FILES_FOLDER

post_parser = reqparse.RequestParser()
post_parser.add_argument('token', dest='token', type=str, required=True, help="User token")
post_parser.add_argument('username', dest='username', type=str, required=True, help="Username")

class UserResource(Resource):

	def post(self):
		args = post_parser.parse_args()

		#Create user

		#Add token to text file
		with open(os.path.join(ROOT_FILES_FOLDER, "credentials.txt")) as myfile:
			myfile.write(args.username + " " + args.token + "\n")

