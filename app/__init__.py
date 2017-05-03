from flask import Flask
import os 
import franz.openrdf

from franz.openrdf.sail.allegrographserver import AllegroGraphServer
from franz.openrdf.repository.repository import Repository
from franz.miniclient import repository
from config import basedir,AG_HOST,AG_PORT,AG_REPOSITORY,AG_USER,AG_PASSWORD

#print config
#Setup app
app = Flask(__name__)
app.config.from_object('config') #Reads the config file located at ../

#setup agraph
server= AllegroGraphServer(AG_HOST, AG_PORT, AG_USER, AG_PASSWORD)
catalog = server.openCatalog()             ## default rootCatalog
#print "Available repositories in catalog '%s':  %s" % (catalog.getName(), catalog.listRepositories())    
myRepository = catalog.getRepository(AG_REPOSITORY, Repository.OPEN)
myRepository.initialize()
dbconAg = myRepository.getConnection()
dedicateddbconAg = myRepository.getConnection()
print "Repository %s is up!  It contains %i statements." % (
	myRepository.getDatabaseName(), dbconAg.size())

from app import api