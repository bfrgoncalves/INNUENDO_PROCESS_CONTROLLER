from app import app
from flask.ext.restful import Api, Resource, reqparse, abort, fields, marshal_with #filters data according to some fields
from flask import jsonify

from flask.ext.security import current_user, login_required, roles_required
import datetime
import subprocess
import os
from config import ROOT_FILES_FOLDER, SEPARATOR

post_parser = reqparse.RequestParser()
post_parser.add_argument('token', dest='token', type=str, required=True, help="User token")
post_parser.add_argument('username', dest='username', type=str, required=True, help="Username")

class UserResource(Resource):

	def post(self):
		args = post_parser.parse_args()

		#Create user

		#Add token to text file
		cred_file = os.path.join(ROOT_FILES_FOLDER, "credentials.txt")
		new_file = os.path.join(ROOT_FILES_FOLDER, 'temp_cred.txt')
		
		if os.path.isfile(cred_file):
			new_token = ""
			new_user_line = ""
			new_file = 'temp_cred.txt'
			with open(new_file, 'w') as tempfile:
			
				with open(cred_file, 'r') as myfile:
					for line in myfile:
						user_line = line.split(SEPARATOR)
						user = line[0]
						token = line[1]
						if user == args.username:
							print 'AQUI'
							new_user_line = user + SEPARATOR + args.token + '\n'
							tempfile.write(new_user_line)
						else:
							tempfile.write(line)
			
			os.remove(cred_file)
			os.rename(new_file, cred_file)
		else:
			with open(cred_file, 'w') as myfile:
				myfile.write(args.username + SEPARATOR + args.token + "\n")

		return { "status": "OK" }

	def get(self):
		print 'AQUI'
		return { "status": "OK" }

