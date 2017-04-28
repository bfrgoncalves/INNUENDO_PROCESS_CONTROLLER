from app import app
from flask.ext.restful import Api, Resource, reqparse, abort, fields, marshal_with #filters data according to some fields
from flask import jsonify, send_file

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

file_get_parser = reqparse.RequestParser()
file_get_parser.add_argument('file_path', dest='file_path', type=str, required=True, help="File_path")


#READ CONFIG FILE
config = {}
execfile("config.py", config)

class DownloadResults(Resource):

	def get(self):
		print "AQUI!!!"
		args = file_get_parser.parse_args()
		try:
			response = send_file(args.file_path, as_attachment=True)
			response.headers.add('Access-Control-Allow-Origin', '*')
			response.headers.add('Content-Type', 'application/force-download')
			return response
		except Exception as e:
			print e
			#self.Error(400)
			return 404



