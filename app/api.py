from app import app
from flask.ext.restful import Api

from resources.jobs.jobs import Job_queue, Test

#Setup API
api = Api(app)

api.add_resource(Job_queue, '/api/v1.0/jobs/')
api.add_resource(Test, '/api/v1.0/jobs/test/')