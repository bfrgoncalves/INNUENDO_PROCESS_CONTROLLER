from app import app
from flask.ext.restful import Api

from resources.jobs.jobs import Job_queue, Test

#Setup API
api = Api(app)

api.add_resource(Job_queue, '/')