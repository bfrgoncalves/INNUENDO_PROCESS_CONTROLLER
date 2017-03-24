from app import app
from flask.ext.restful import Api

from resources.jobs.jobs import Job_queue
from resources.files.files import FilesResource

#Setup API
api = Api(app)

api.add_resource(Job_queue, '/jobs/')

#get files from user
api.add_resource(FilesResource, '/fastqs/')