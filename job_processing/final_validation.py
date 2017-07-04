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

from config import core_headers_correspondece, wg_headers_correspondece

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

print core_headers_correspondece

#wg_headers_correspondece = config["cg_headers_correspondece"]
#cg_headers_correspondece = config["cg_headers_correspondece"]

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

	with open(file_path, 'r') as info_file:
		for line in info_file:
			json_file = json.loads(line)
			for key, val in json_file.iteritems():
				return val["pass_qc"]


def validate_chewbbaca(procedure, file_path, specie):

	allele_classes_to_ignore = {'LNF': '0', 'INF-': '', 'NIPHEM': '0', 'NIPH': '0', 'LOTSC': '0', 'PLOT3': '0', 'PLOT5': '0', 'ALM': '0', 'ASM': '0'}

	core_profile = []

	with open(file_path, 'r') as chewBBACA_info_file:
		for line in chewBBACA_info_file:
			json_file = json.loads(line)
			profile = json_file["run_output.fasta"]
			headers = json_file["header"]

			with open(core_headers_correspondece[specie], 'r') as reader:
				for i, line in enumerate(reader):
					count_core+=1
					if line.rstrip() == "FILE":
						continue
					else:
						include_index = headers.index(line.rstrip())
						if include_index > -1:
							core_profile.append(profile[include_index])
			
			to_string = ",".join(core_profile)
			for k,v in allele_classes_to_ignore.iteritems():
				to_string = to_string.replace(k,v)
			to_array = to_string.split(",")

			count_missing = 0
			for x in to_array:
				if x == "0":
					count_missing += 1

			percentage_missing = (float(count_missing)/float(len(to_array)))
			print percentage_missing
			#for key, val in json_file.iteritems():
			#	return val["pass_qc"]


def main():

	parser = argparse.ArgumentParser(prog='final_validation.py', description='Validates the programs outputs and set warnings or not')

	parser.add_argument('--file_path_to_validate', type=str, help='File to be used as validation', required=True)
	parser.add_argument('--procedure', type=str, help='File to be used as validation', required=True)
	parser.add_argument('--specie', type=str, help='Species to apply and make correpondence with chewbbaca core gene list', required=False)

	args = parser.parse_args()

	if args.procedure == 'INNUca':
		status = validate_innuca(args.procedure, args.file_path_to_validate)
		if str(status) == str("True"):
			sys.stdout.write("True")
		else:
			sys.stdout.write("WARNING")
	elif args.procedure == 'chewBBACA' and args.specie:
		status = validate_chewbbaca(args.procedure, args.file_path_to_validate, args.specie)
		if str(status) == str("True"):
			sys.stdout.write("True")
		else:
			sys.stdout.write("WARNING")
	elif args.procedure == 'PathoTyping':
		status = validate_pathotyping(args.procedure, args.file_path_to_validate)




if __name__ == "__main__":
	main()