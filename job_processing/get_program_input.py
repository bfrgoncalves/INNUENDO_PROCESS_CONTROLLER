import os
import requests
import argparse

from queryParse2Json import parseAgraphStatementsRes,parseAgraphQueryRes

#from config import obo,localNSpace,protocolsTypes,processTypes,processMessages
from franz.openrdf.vocabulary.rdf import RDF
from franz.openrdf.vocabulary.xmlschema import XMLSchema
from franz.openrdf.query.query import QueryLanguage
from franz.openrdf.model import URI

#READ CONFIG FILE
config = {}
execfile("config.py", config)

obo = config["obo"]
localNSpace = config["localNSpace"]
protocolsTypes = config["protocolsTypes"]
processTypes = config["processTypes"]
processMessages = config["processMessages"]

def get_process_input(project_id, pipeline_id, process_id):

	try:
		procStr = localNSpace + "projects/" + str(project_id) + "/pipelines/" + str(pipeline_id) + "/processes/" + str(process_id)
		queryString = "SELECT ?file1 ?file2 ?file3   WHERE {<"+procStr+"> obo:RO_0002233 ?in. ?in obo:NGS_0000092 ?file1.?in obo:NGS_0000093 ?file2.?in obo:NGS_0000094 ?file3.}"
		#print queryString
		tupleQuery = dbconAg.prepareTupleQuery(QueryLanguage.SPARQL, queryString)
		result = tupleQuery.evaluate()
		
		jsonResult=parseAgraphQueryRes(result,["file3"])
		print jsonResult
		
		'''file_out = ""
		for bindingSet in result:
			print bindingSet
			file_out = bindingSet["file3"] #output_file
		'''
		result.close()

		
		return jsonResult, 200
	except Exception as e:
		print e
		return 404



def set_process_output(project_id, pipeline_id, process_id, output):

	try:
		#Agraph
		processURI = dbconAg.createURI(namespace=localNSpace+"projects/", localname=str(project_id)+"/pipelines/"+str(pipeline_id)+"/processes/"+str(process_id))


		#get output URI from process
		hasOutput = dbconAg.createURI(namespace=obo, localname="RO_0002234")
		statements = dbconAg.getStatements(processURI, hasOutput, None)
		outputURI=parseAgraphStatementsRes(statements)
		statements.close()

		outputURI = dbconAg.createURI(outputURI[0]['obj'])

		runInfo = dbconAg.createLiteral((args.run_info), datatype=XMLSchema.STRING)
		runInfoProp = dbconAg.createURI(namespace=obo, localname="NGS_0000092")

		runStats = dbconAg.createLiteral((args.run_stats), datatype=XMLSchema.STRING)
		runStatsProp = dbconAg.createURI(namespace=obo, localname="NGS_0000093")

		runFile = dbconAg.createLiteral((args.output), datatype=XMLSchema.STRING)
		runFileProp = dbconAg.createURI(namespace=obo, localname="NGS_0000094")

		dbconAg.remove(outputURI, runInfoProp, None)
		dbconAg.remove(outputURI, runStatsProp, None)
		dbconAg.remove(outputURI, runFileProp, None)

		#add outputs paths to process
		stmt1 = dbconAg.createStatement(outputURI, runInfoProp, runInfo)
		stmt2 = dbconAg.createStatement(outputURI, runStatsProp, runStats)
		stmt3 = dbconAg.createStatement(outputURI, runFileProp, runFile)

		#send to allegro
		dbconAg.add(stmt1)
		dbconAg.add(stmt2)
		dbconAg.add(stmt3)
		return 202
	except Exception as e:
		print e
		return 404


def main():

	parser = argparse.ArgumentParser(prog='get_program_input.py', description='Sets and Gets process inputs and outputs')

	parser.add_argument('--process', type=str, help='Process identifier', required=True)
	parser.add_argument('--pipeline', type=str, help='Pipeline identifier', required=True)
	parser.add_argument('--project', type=str, help='Project identifier', required=True)
	parser.add_argument('-v1', type=str, help='path value for file1', required=False)
	parser.add_argument('-v2', type=str, help='path value for file2', required=False)
	parser.add_argument('-v3', type=str, help='path value for file3', required=False)
	parser.add_argument('-t', type=str, help='type of set (input or output)', required=True)

	args = parser.parse_args()

	if args.t == 'output' and not args.v1:
		get_process_output(args.project, args.pipeline, args.process)
	elif args.t == 'input' and not args.v1:
		get_process_input(args.project, args.pipeline, args.process)
	elif args.t == 'output' and args.v1:
		set_process_output(args.project, args.pipeline, args.process, args.v1, args.v2, args.v3)
	elif args.t == 'input' and args.v1:
		set_process_input(args.project, args.pipeline, args.process, args.v1, args.v2, args.v3)



if __name__ == "__main__":
	main()