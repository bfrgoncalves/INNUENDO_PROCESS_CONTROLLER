from app import app
from flask.ext.restful import Api, Resource, reqparse, abort, fields, marshal_with #filters data according to some fields
from flask import jsonify
import glob, os

file_get_parser = reqparse.RequestParser()
file_get_parser.add_argument('username', dest='username', type=str, required=True, help="Username")

config1 = {}
execfile("config.py", config1)

class FilesResource(Resource):

	def get(self):

		args = file_get_parser.parse_args()
		files_folder = os.path.join('/home/users/', args.username, config['FTP_FILES_FOLDER'], '*')
		for fl in glob.glob(files_folder):
		    print fl
		
		return 200