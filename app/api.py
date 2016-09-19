from app import app
from flask.ext.restful import Api

from resources.users import UserResource

#Setup Controller API
api = Api(app)

#CREATE USER CONTROLLER
api.add_resource(UserResource, '/controller/v1.0/users', endpoint = 'controller_users')
