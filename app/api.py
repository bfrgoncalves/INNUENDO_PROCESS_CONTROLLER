from app import app
from flask.ext.restful import Api

from resources.jobs.jobs import Job_queue, FilesResource, DownloadFilesResource, CopyChewSchema
from resources.downloads.downloads import DownloadResults

#Setup API
api = Api(app)

api.add_resource(Job_queue, '/jobs/')

#get files from user
api.add_resource(FilesResource, '/jobs/fastqs/')

#download files to user area
api.add_resource(DownloadFilesResource, '/jobs/download/')

#download files to user area
api.add_resource(DownloadResults, '/jobs/results/download/')

#get files from user
api.add_resource(CopyChewSchema, '/jobs/schema/copy')