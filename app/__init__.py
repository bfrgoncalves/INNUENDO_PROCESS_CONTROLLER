from flask import Flask
import os 

from franz.openrdf.sail.allegrographserver import AllegroGraphServer
from franz.openrdf.repository.repository import Repository
from franz.miniclient import repository
from config import basedir,AG_HOST,AG_PORT,AG_REPOSITORY,AG_USER,AG_PASSWORD

from queryParse2Json import parseAgraphStatementsRes,parseAgraphQueryRes

#from config import obo,localNSpace,protocolsTypes,processTypes,processMessages

#print config
#Setup app
app = Flask(__name__)
app.config.from_object('config') #Reads the config file located at ../


from app import api