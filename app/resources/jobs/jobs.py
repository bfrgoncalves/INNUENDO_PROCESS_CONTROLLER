from app import dbconAg
from flask_restful import Resource, reqparse
from flask import request
from job_processing.queue_processor import Queue_Processor
from job_processing.queryParse2Json import parseAgraphStatementsRes

from franz.openrdf.vocabulary.xmlschema import XMLSchema

import json
import subprocess
import os
import glob
import sys

job_post_parser = reqparse.RequestParser()
job_post_parser.add_argument('data', dest='data', type=str, required=True,
                             help="Job Parameters")
job_post_parser.add_argument('current_specie', dest='current_specie', type=str,
                             required=True, help="Current Specie")
job_post_parser.add_argument('sampleName', dest='sampleName', type=str,
                             required=True, help="Sample Name")
job_post_parser.add_argument('current_user_name', dest='current_user_name',
                             type=str, required=True, help="Current user name")
job_post_parser.add_argument('current_user_id', dest='current_user_id',
                             type=str, required=True, help="current user id")
job_post_parser.add_argument('homedir', dest='homedir', type=str, required=True,
                             help="home dir")

job_get_parser = reqparse.RequestParser()
job_get_parser.add_argument('job_id', dest='job_id', type=str, required=True,
                            help="Job ID")
job_get_parser.add_argument('project_id', dest='project_id', type=str,
                            required=True, help="project_id ID")
job_get_parser.add_argument('pipeline_id', dest='pipeline_id', type=str,
                            required=True, help="pipeline_id ID")
job_get_parser.add_argument('process_id', dest='process_id', type=str,
                            required=True, help="process_id ID")
job_get_parser.add_argument('username', dest='username', type=str,
                            required=True, help="Username")
job_get_parser.add_argument('homedir', dest='homedir', type=str, required=True,
                            help="Home dir")
job_get_parser.add_argument('from_process_controller',
                            dest='from_process_controller', type=str,
                            required=True, help="from_process_controller")

job_put_parser = reqparse.RequestParser()
job_put_parser.add_argument('project_id', dest='project_id', type=str,
                            required=True, help="project_id ID")
job_put_parser.add_argument('pipeline_id', dest='pipeline_id', type=str,
                            required=True, help="pipeline_id ID")
job_put_parser.add_argument('process_id', dest='process_id', type=str,
                            required=True, help="process_id ID")
job_put_parser.add_argument('run_property', dest='run_property', type=str,
                            required=True, help="Username")
job_put_parser.add_argument('run_property_value', dest='run_property_value',
                            type=str, required=True, help="Username")
job_put_parser.add_argument('type', dest='type', type=str, required=True,
                            help="Username")

file_get_parser = reqparse.RequestParser()
file_get_parser.add_argument('username', dest='username', type=str,
                             required=True, help="Username")
file_get_parser.add_argument('homedir', dest='homedir', type=str,
                             required=True, help="Home dir")

download_file_get_parser = reqparse.RequestParser()
download_file_get_parser.add_argument('username', dest='username', type=str,
                                      required=True, help="Username")
download_file_get_parser.add_argument('accession_numbers',
                                      dest='accession_numbers', type=str,
                                      required=True, help="Accession numbers")

copy_schema_get_parser = reqparse.RequestParser()
copy_schema_get_parser.add_argument('schema_to_copy', dest='schema_to_copy',
                                    type=str, required=True,
                                    help="chewBBACA schema to copy")

inspect_get_parser = reqparse.RequestParser()
inspect_get_parser.add_argument('pipeline_id', dest='pipeline_id',
                                type=str, required=True,
                                help="pipeline_id")
inspect_get_parser.add_argument('project_id', dest='project_id',
                                type=str, required=True,
                                help="project_id")
inspect_get_parser.add_argument('homedir', dest='homedir',
                                type=str, required=True,
                                help="homedir")

inspect_post_parser = reqparse.RequestParser()
inspect_post_parser.add_argument('pipeline_id', dest='pipeline_id',
                                 type=str, required=True,
                                 help="pipeline_id")
inspect_post_parser.add_argument('project_id', dest='project_id',
                                 type=str, required=True,
                                 help="project_id")
inspect_post_parser.add_argument('homedir', dest='homedir',
                                 type=str, required=True,
                                 help="homedir")

inspect_put_parser = reqparse.RequestParser()
inspect_put_parser.add_argument('pid', dest='pid',
                                type=str, required=True,
                                help="pid")

params_get_parser = reqparse.RequestParser()
params_get_parser.add_argument('selected_param', dest='selected_param',
                               type=str, required=True,
                               help="selected_param")

workflow_test_post_parser = reqparse.RequestParser()
workflow_test_post_parser.add_argument('protocols', dest='protocols',
                                       type=str, required=True,
                                       help="protocols")

# READ CONFIG FILE
config = {}
execfile("config.py", config)

obo = config["obo"]
localNSpace = config["localNSpace"]
protocolsTypes = config["protocolsTypes"]
processTypes = config["processTypes"]
processMessages = config["processMessages"]


class CheckControllerResource(Resource):
    def get(self):
        return True


class Job_queue(Resource):
    def post(self):
        args = job_post_parser.parse_args()
        job_parameters = args.data
        current_specie = args.current_specie
        sampleName = args.sampleName
        current_user_name = args.current_user_name
        current_user_id = args.current_user_id

        innuendo_processor = Queue_Processor()
        jobID, code = innuendo_processor.insert_job(
            job_parameters=job_parameters, current_specie=current_specie,
            sampleName=sampleName, current_user_name=current_user_name,
            current_user_id=current_user_id, homedir=args.homedir)

        return {'jobID': jobID, 'code': code}, 200

    def get(self):
        args = job_get_parser.parse_args()

        job_ids = args.job_id.split(",")
        process_ids = args.process_id.split(",")
        store_jobs_in_db = []
        all_results = []
        all_std_out = []
        all_paths = []

        for k in range(0, len(job_ids)):
            job_id = job_ids[k]
            process_id = process_ids[k]

            results = [[], []]
            store_in_db = False

            print '--project ' + args.project_id + ' --pipeline ' + \
                  args.pipeline_id + ' --process ' + process_id + ' -t status'

            commands = 'python job_processing/get_program_input.py --project ' \
                       + args.project_id + ' --pipeline ' + args.pipeline_id + \
                       ' --process ' + process_id + ' -t status'

            proc1 = subprocess.Popen(commands.split(' '),
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)

            stdout, stderr = proc1.communicate()

            if stderr:
                print stderr

            stdout = job_id + '\t' + stdout

            all_std_out.append(stdout)
            store_jobs_in_db.append(store_in_db)
            all_results.append(results[0])
            all_paths.append(results[1])

        return {'stdout': all_std_out, 'store_in_db': store_jobs_in_db,
                'results': all_results, 'paths': all_paths, 'job_id': job_ids}


class FilesResource(Resource):
    def get(self):
        args = file_get_parser.parse_args()
        files_folder = os.path.join(args.homedir, config['FTP_FILES_FOLDER'],
                                    '*.gz')
        v_files = []
        for fl in glob.glob(files_folder):
            v_files.append(os.path.basename(fl))

        return {'files': sorted(v_files)}, 200


class DownloadFilesResource(Resource):
    def post(self):
        args = download_file_get_parser.parse_args()
        innuendo_processor = Queue_Processor()
        output = innuendo_processor.download_accessions(
            download_parameters=args)

        return output, 200

    def get(self):
        args = download_file_get_parser.parse_args()
        file_array = []
        file_folder = os.path.join('/home/users/', args.username,
                                   config['FTP_FILES_FOLDER'],
                                   args.accession_numbers)

        with open(file_folder, 'r') as file_to_send:
            for line in file_to_send:
                file_array.append(line)

        return {'output': file_array}, 200


# DEPRECATED ###############
class CopyChewSchema(Resource):
    def get(self):
        args = copy_schema_get_parser.parse_args()

        commands = ['cp', '-r',
                    './dependencies/chewBBACA/chewBBACA_schemas_on_compute/' +
                    args.schema_to_copy,
                    './dependencies/chewBBACA/chewBBACA_schemas/' +
                    args.schema_to_copy + '_new']

        proc = subprocess.Popen(commands, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        proc.communicate()

        commands = ['rm', '-rf',
                    './dependencies/chewBBACA/chewBBACA_schemas/' +
                    args.schema_to_copy]

        proc = subprocess.Popen(commands, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        proc.communicate()

        commands = ['mv', './dependencies/chewBBACA/chewBBACA_schemas/' +
                    args.schema_to_copy + '_new',
                    './dependencies/chewBBACA/chewBBACA_schemas/' +
                    args.schema_to_copy]

        proc = subprocess.Popen(commands, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        proc.communicate()

        return 200


class SetNGSOntoOutput(Resource):
    def post(self):

        parameters = request.json
        parameters_json = json.loads(parameters.replace("'", '"'))

        def set_process_output(project_id, pipeline_id, process_id, run_info,
                               run_stats, output, log_file, status):

            try:
                # Agraph
                processURI = dbconAg.createURI(
                    namespace=localNSpace + "projects/",
                    localname=str(project_id) + "/pipelines/" + str(
                        pipeline_id) + "/processes/" + str(process_id))

                # get output URI from process
                hasOutput = dbconAg.createURI(namespace=obo,
                                              localname="RO_0002234")
                statements = dbconAg.getStatements(processURI, hasOutput, None)
                outputURI = parseAgraphStatementsRes(statements)
                statements.close()

                outputURI = dbconAg.createURI(outputURI[0]['obj'])

                runInfo = dbconAg.createLiteral((run_info),
                                                datatype=XMLSchema.STRING)
                runInfoProp = dbconAg.createURI(namespace=obo,
                                                localname="NGS_0000092")

                runStats = dbconAg.createLiteral((run_stats),
                                                 datatype=XMLSchema.STRING)
                runStatsProp = dbconAg.createURI(namespace=obo,
                                                 localname="NGS_0000093")

                runFile = dbconAg.createLiteral((output),
                                                datatype=XMLSchema.STRING)

                runFileProp = dbconAg.createURI(namespace=obo,
                                                localname="NGS_0000094")

                logFile = dbconAg.createLiteral((log_file),
                                                datatype=XMLSchema.STRING)

                logFileProp = dbconAg.createURI(namespace=obo,
                                                localname="NGS_0000096")

                runStatus = dbconAg.createLiteral((status),
                                                  datatype=XMLSchema.STRING)

                runStatusProp = dbconAg.createURI(namespace=obo,
                                                  localname="NGS_0000097")

                dbconAg.remove(outputURI, runInfoProp, None)
                dbconAg.remove(outputURI, runStatsProp, None)
                dbconAg.remove(outputURI, runFileProp, None)
                dbconAg.remove(outputURI, runStatusProp, None)

                # add outputs paths to process
                stmt1 = dbconAg.createStatement(outputURI, runInfoProp,
                                                runInfo)

                stmt2 = dbconAg.createStatement(outputURI, runStatsProp,
                                                runStats)

                stmt3 = dbconAg.createStatement(outputURI, runFileProp,
                                                runFile)

                stmt4 = dbconAg.createStatement(outputURI, logFileProp, logFile)

                stmt5 = dbconAg.createStatement(outputURI, runStatusProp,
                                                runStatus)

                # send to allegro
                dbconAg.add(stmt1)
                dbconAg.add(stmt2)
                dbconAg.add(stmt3)
                dbconAg.add(stmt4)
                dbconAg.add(stmt5)

            except Exception as e:
                print "ERROR", e

        set_process_output(parameters_json["project_id"],
                           parameters_json["pipeline_id"],
                           parameters_json["process_id"],
                           parameters_json["run_info"],
                           parameters_json["warnings"],
                           parameters_json["run_output"],
                           parameters_json["log_file"],
                           parameters_json["status"])

        return 200

    def put(self):
        parameters = request.json
        parameters_json = json.loads(parameters.replace("'", '"'))

        def set_unique_prop_output(project_id, pipeline_id, process_id,
                                   property_type, property_value):

            output_prop_to_type = {
                "run_info": "NGS_0000092", "run_output": "NGS_0000093",
                "warnings": "NGS_0000094", "log_file": "NGS_0000096",
                "status": "NGS_0000097"
            }

            property_types = property_type.split(",")
            property_values = property_value.split(",")

            try:
                for p, v in zip(property_types, property_values):
                    # Agraph
                    processURI = dbconAg.createURI(
                        namespace=localNSpace + "projects/",
                        localname=str(project_id) + "/pipelines/" + str(
                            pipeline_id) + "/processes/" + str(process_id))

                    # get output URI from process
                    hasOutput = dbconAg.createURI(namespace=obo,
                                                  localname="RO_0002234")
                    statements = dbconAg.getStatements(processURI,
                                                       hasOutput, None)
                    outputURI = parseAgraphStatementsRes(statements)
                    statements.close()

                    outputURI = dbconAg.createURI(outputURI[0]['obj'])

                    runInfo = dbconAg.createLiteral((v),
                                                    datatype=XMLSchema.STRING)

                    runInfoProp = dbconAg.createURI(
                        namespace=obo, localname=output_prop_to_type[p])

                    if p != "log_file" and p != "warnings":
                        dbconAg.remove(outputURI, runInfoProp, None)

                    # add outputs paths to process
                    stmt1 = dbconAg.createStatement(outputURI, runInfoProp,
                                                    runInfo)

                    # send to allegro
                    dbconAg.add(stmt1)

            except Exception as e:
                print e

        set_unique_prop_output(parameters_json["project_id"],
                               parameters_json["pipeline_id"],
                               parameters_json["process_id"],
                               parameters_json["run_property"],
                               parameters_json["run_property_value"])

        return 200


class FlowcraftInspect(Resource):
    def get(self):

        args = inspect_get_parser.parse_args()

        commands = ['sh',
                    './job_processing/bash_scripts/trigger_inspect.sh',
                    args.homedir,
                    args.project_id,
                    args.pipeline_id,
                    config["INSPECT_ROUTE"]
                    ]

        link = ""
        pid = ""

        process = subprocess.Popen(commands, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        count = 0

        for line in iter(process.stdout.readline, ''):
            sys.stdout.write(line)

            if "http" in line:
                link = line
                count += 1
            if "pid:" in line:
                pid = line
                count += 1

            if count == 2:
                return {"link": link, "pid": pid}

    def put(self):

        args = inspect_put_parser.parse_args()

        commands = ['sh',
                    './job_processing/bash_scripts/kill_inspect.sh',
                    args.pid
                    ]

        process = subprocess.Popen(commands, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        return True

    def post(self):

        args = inspect_post_parser.parse_args()

        executor_path = os.path.join(args.homedir, "jobs",
                                     args.project_id + "-" + args.pipeline_id,
                                     "executor_command.txt")

        commands = ['sh',
                    './job_processing/bash_scripts/retry_pipeline.sh',
                    executor_path
                    ]

        process = subprocess.Popen(commands, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        stdout, stderr = process.communicate()

        print stdout, stderr

        return True


class FlowcraftParams(Resource):
    def get(self):
        args = params_get_parser.parse_args()

        commands = ['sh',
                    './job_processing/bash_scripts/check_flowcraft_params.sh',
                    args.selected_param
                    ]

        process = subprocess.Popen(commands, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        tosend = False

        stdout, stderr = process.communicate()

        print stdout
        print stderr

        if stderr == "":
            tosend = stdout

        return {"stdout": str(tosend)}


class FlowcraftBuildTest(Resource):
    def post(self):
        args = workflow_test_post_parser.parse_args()

        commands = ['sh',
                    './job_processing/bash_scripts/test_flowcraft_build.sh',
                    " ".join(args.protocols.split(","))
                    ]

        process = subprocess.Popen(commands, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        stdout, stderr = process.communicate()

        if stderr:
            print stderr

        return {"stdout": str(stdout)}
