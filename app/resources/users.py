from app import app
from flask.ext.restful import Api, Resource, reqparse, abort, fields, marshal_with #filters data according to some fields
from flask import jsonify

from flask.ext.security import current_user, login_required, roles_required
import datetime
import subprocess
import os
from config import ROOT_CREDENTIALS_FOLDER, SEPARATOR
from app.utils.user_utils import create_user, random_letters, changepass

post_parser = reqparse.RequestParser()
post_parser.add_argument('username', dest='username', type=str, required=True, help="Username")

class UserResource(Resource):

	def post(self):
		args = post_parser.parse_args()
		rl = random_letters(20)
		#Add token to text file
		cred_file = os.path.join(ROOT_CREDENTIALS_FOLDER, "credentials.txt")
		new_file = os.path.join(ROOT_CREDENTIALS_FOLDER, 'temp_cred.txt')

		new_username = args.username.split('@')[0]
		upload_pass = ""
		
		if os.path.isfile(cred_file):
			new_token = ""
			new_user_line = ""
			new_file = 'temp_cred.txt'
			added = False
			with open(new_file, 'w') as tempfile:
			
				with open(cred_file, 'r') as myfile:
					for line in myfile:
						user_line = line.split(SEPARATOR)
						user = user_line[0]
						folder_name = user_line[1]

						if user == new_username:
							upload_pass = changepass(new_username)
							new_user_line = user + SEPARATOR + folder_name + SEPARATOR + upload_pass + '\n'
							tempfile.write(new_user_line)
							added = True
						else:
							tempfile.write(line)
			if not added:
				with open(new_file, 'a') as tempfile:
					upload_pass = create_user(new_username, rl)
					tempfile.write(new_username + SEPARATOR + rl + SEPARATOR + upload_pass + "\n")

			
			os.remove(cred_file)
			os.rename(new_file, cred_file)
		else:
			with open(cred_file, 'w') as myfile:
				upload_pass = create_user(new_username, rl)
				myfile.write(new_username + SEPARATOR + rl + SEPARATOR + upload_pass + "\n")
				create_user(new_username, rl)

		return { "upload_pass": upload_pass }

	def get(self):
		return { "status": "OK" }

