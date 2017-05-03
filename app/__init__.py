from flask import Flask
import os 
import franz.openrdf

from franz.openrdf.sail.allegrographserver import AllegroGraphServer
from franz.openrdf.repository.repository import Repository
from franz.miniclient import repository
from config import basedir,AG_HOST,AG_PORT,AG_REPOSITORY,AG_USER,AG_PASSWORD

#from queryParse2Json import parseAgraphStatementsRes,parseAgraphQueryRes

#from config import obo,localNSpace,protocolsTypes,processTypes,processMessages

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
#dbconAg = myRepository.getConnection()
#dedicateddbconAg = myRepository.getConnection()
print "Repository %s is up!  It contains %i statements." % (
	myRepository.getDatabaseName(), dbconAg.size())

print '####################################################'

from franz.openrdf.vocabulary.rdf import RDF
from franz.openrdf.vocabulary.xmlschema import XMLSchema
from franz.openrdf.query.query import QueryLanguage
from franz.openrdf.model import URI

print "BABABAB"

from app import api