import os
import requests
import argparse
import sys

from queryParse2Json import parseAgraphStatementsRes,parseAgraphQueryRes

#from config import obo,localNSpace,protocolsTypes,processTypes,processMessages
import os 
import json

from franz.openrdf.sail.allegrographserver import AllegroGraphServer
from franz.openrdf.repository.repository import Repository
from franz.miniclient import repository

#READ CONFIG FILE
config = {}
execfile("config.py", config)

obo = config["obo"]
localNSpace = config["localNSpace"]
protocolsTypes = config["protocolsTypes"]
processTypes = config["processTypes"]
processMessages = config["processMessages"]
basedir = config["basedir"]
AG_HOST = config["AG_HOST"]
AG_PORT = config["AG_PORT"]
AG_REPOSITORY = config["AG_REPOSITORY"]
AG_USER = config["AG_USER"]
AG_PASSWORD = config["AG_PASSWORD"]

from queryParse2Json import parseAgraphStatementsRes,parseAgraphQueryRes

#setup agraph
server= AllegroGraphServer(AG_HOST, AG_PORT, AG_USER, AG_PASSWORD)
catalog = server.openCatalog()             ## default rootCatalog
#print "Available repositories in catalog '%s':  %s" % (catalog.getName(), catalog.listRepositories())    
myRepository = catalog.getRepository(AG_REPOSITORY, Repository.OPEN)
myRepository.initialize()
dbconAg = myRepository.getConnection()
dedicateddbconAg = myRepository.getConnection()
#print "Repository %s is up!  It contains %i statements." % (
#	myRepository.getDatabaseName(), dbconAg.size())

#print '####################################################'

from franz.openrdf.vocabulary.rdf import RDF
from franz.openrdf.vocabulary.xmlschema import XMLSchema
from franz.openrdf.query.query import QueryLanguage
from franz.openrdf.model import URI


def validate_innuca(procedure, file_path):

	with open(file_path, r) as info_file:
		for line in reader:
			json_file = json.loads(line)
			print json_file
			for key, val in json_file.iteritems():
				print val["pass_qc"]




def main():

	parser = argparse.ArgumentParser(prog='final_validation.py', description='Validates the programs outputs and set warnings or not')

	parser.add_argument('--file_path_to_validate', type=str, help='File to be used as validation', required=True)
	parser.add_argument('--procedure', type=str, help='File to be used as validation', required=True)

	args = parser.parse_args()

	if args.procedure == 'INNUca':
		status = validate_innuca(args.procedure, args.file_path_to_validate)
	elif args.procedure == 'chewBBACA':
		status = validate_chewbbaca(args.procedure, args.file_path_to_validate)
	elif args.procedure == 'PathoTyping':
		status = validate_pathotyping(args.procedure, args.file_path_to_validate)




if __name__ == "__main__":
	main()