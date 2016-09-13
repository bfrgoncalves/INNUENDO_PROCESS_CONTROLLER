from app import app
from flask.ext.restful import Api

from resources.jobs import JobsResource, JobResource, JobStatusResource
from resources.files import UserFilesResource


#Setup Controller API
api = Api(app)

#Jobs controllers
api.add_resource(JobsResource, '/api/v1.0/jobs/', endpoint = 'jobs')
api.add_resource(JobResource, '/api/v1.0/jobs/<int:id>', endpoint = 'single_job')
api.add_resource(JobStatusResource, '/api/v1.0/jobs/<int:id>/status/', endpoint = 'single_job_status')

#Files controllers
api.add_resource(UserFilesResource, '/api/v1.0/files/', endpoint = 'files')