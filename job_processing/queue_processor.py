from rq import Queue
from redis import Redis
import subprocess
import os
import json
import string
import random
import ast

# READ CONFIG FILE
config = {}
execfile("config.py", config)

redis_conn = Redis()
q = Queue('innuendo_jobs', connection=redis_conn)


def setFilesByProgram(key_value_args, workflow):

    wf_params = json.loads(workflow['parameters'])
    if wf_params['used Software'] in config['APPLICATIONS_ARRAY']:
        software = wf_params['used Software']
        softwarePath = config['FILETYPES_SOFTWARE'][software][0]['path']
        language = config['FILETYPES_SOFTWARE'][software][0]['language']
        return key_value_args, softwarePath, language
    else:
        return False, False


def write_config_file(file_instance, write_object):

    file_instance.write("params {\n")

    for key, val in write_object.items():
        to_write = ""

        isArray = False

        try:
            print ast.literal_eval(str(val))
            if type(ast.literal_eval(str(val))) is list:
                isArray = True
        except Exception:
            isArray = False

        if val == "true" or val == "false" or val == "null" or isArray:
            to_write = '{}={}\n'
        else:
            to_write = '{}="{}"\n'

        file_instance.write(to_write.format(key, val))

    file_instance.write("}")


def submitToSLURM(user_folder, workflow_path_array, numberOfWorkflows,
                  array_of_files, software, dependency_id, slurm_cpus):
    array_to_string = '\#'.join(workflow_path_array)

    array_tasks = []
    count_tasks = 0
    total_tasks = 1

    has_dependency = False

    random_sbatch_number = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for _ in range(6))

    for a in range(0, numberOfWorkflows):
        array_tasks.append(str(count_tasks))
        count_tasks += 1
        total_tasks += 1

    # launch different template depending on the procedure (case of
    #  dependencies)
    if software == "chewBBACA":
        to_dependency = '1'
        if dependency_id is not None:
            to_dependency = dependency_id
        commands = ['sh', 'job_processing/launch_job_chewbbaca.sh'] +\
                   [array_to_string, ','.join(array_of_files), user_folder,
                    str(random_sbatch_number), to_dependency, slurm_cpus]
    else:
        commands = ['sh', 'job_processing/launch_job.sh'] + \
                   [array_to_string, ','.join(array_of_files),
                    user_folder, str(random_sbatch_number), slurm_cpus]

    if software == "INNUca":
        has_dependency = True

    proc = subprocess.Popen(commands, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    stdout, stderr = proc.communicate()
    jobID = stdout.split(' ')
    jobID = jobID[-1].strip('\n')

    return jobID, array_tasks, has_dependency


def extract_ids(job_out):
    job_out = job_out.split('\n')
    tasks = []

    for x in job_out:
        if '[' in x:
            job_id = x.split('_')[0]
            task_ids = x.split('[')[1].split(']')[0].split('-')
            for k in range(int(task_ids[0]), int(task_ids[1])+1):
                tasks.append(job_id + '_' + str(k))
        elif x != '':
            tasks.append(x)

    return tasks


class Queue_Processor:

    def process_job(self, job_parameters, current_specie, sampleName,
                    current_user_name, current_user_id, homedir):

        job_parameters = json.loads(job_parameters)

        count_workflows = 0
        nextflow_tags = []
        writeCacheFile = True

        task_ids = []
        processIDs = []

        # Dictionary with params associated with a process
        processToParams = {}

        # To send to nextflow generator
        project_id = ""
        pipeline_id = ""
        nexflow_user_dir = ""
        asperaKey = ""
        accessionsPath = ""

        random_pip_name = job_parameters[0]['project_id']+'_' + \
                          job_parameters[0]['pipeline_id'] + ".nf"

        for workflow in job_parameters:
            # Load data retrieved from the queue process
            count_workflows += 1
            parameters = json.loads(workflow['parameters'])['used Parameter']
            files = json.loads(workflow['files'])
            strain_submitter = workflow['strain_submitter']
            nextflow_tag = json.loads(workflow['parameters'])['Nextflow Tag']
            project_id = workflow['project_id']
            pipeline_id = workflow['pipeline_id']
            process_id = workflow['process_id']
            process_to_run = workflow['process_to_run']
            image = json.loads(workflow['parameters'])['Image']
            cpus = json.loads(workflow['parameters'])['CPUs']
            memory = json.loads(workflow['parameters'])['Memory']

            print image, cpus, memory

            nexflow_user_dir = os.path.join(homedir, "jobs", project_id+"-"+
                                            pipeline_id)

            process_identifier = nextflow_tag + "_" + process_id

            # Check if key not already in params dict
            if process_identifier not in processToParams.keys():
                processToParams[process_identifier] = {}

            # Case failed on previous chewbbaca steps
            if "chewbbaca" in nextflow_tag and process_to_run == "false":
                continue

            # Case process is mlst, needs to get the species correspondence
            # from the configuration file if not added by the user upon
            # protocol creation
            if "mlst" in nextflow_tag:
                processToParams[process_identifier]['mlstSpecies'] = config[
                    "MLST_CORRESPONDENCE"][current_specie]

            # Case downloading reads, it requires the aspera key if not
            # provided by the user upon protocol creation and the path
            # to the file with the accession numbers
            if "reads_download" in nextflow_tag:
                processToParams[process_identifier]['asperaKey'] = config["ASPERAKEY"]
                processToParams[process_identifier]['accessions'] = \
                    os.path.join(nexflow_user_dir, "accessions.txt")
                accessionsPath = os.path.join(nexflow_user_dir, "accessions.txt")

            # Case the process is chewbbaca, it requires training files,
            # schema, loci list if not provided by the admin upon protocol
            # creation
            if "chewbbaca" in nextflow_tag:
                processToParams[process_identifier]['chewbbacaTraining'] = \
                    config["CHEWBBACA_TRAINING_FILE"][current_specie]
                processToParams[process_identifier]['schemaPath'] = \
                    os.path.join(
                    config["CHEWBBACA_SCHEMAS_PATH"], parameters["schemaPath"])
                processToParams[process_identifier]['schemaSelectedLoci'] = \
                    os.path.join(
                    config["CHEWBBACA_SCHEMAS_PATH"], parameters["schemaPath"],
                    "listGenes.txt")
                processToParams[process_identifier]['schemaCore'] = \
                    config[
                    "core_headers_correspondece"][parameters["schemaVersion"]][current_specie]
                processToParams[process_identifier]['chewbbacaJson'] = 'true'

            # Case process is seq_typing, it requires the reference files or
            # target finding if not provided by the admin upon protocol creation
            if "seq_typing" in nextflow_tag:
                processToParams[process_identifier]['referenceFileO'] = config[
                    "SEQ_FILE_O"][current_specie]
                processToParams[process_identifier]['referenceFileH'] = config[
                    "SEQ_FILE_H"][current_specie]

            # If patho_typing or true_coverage, it requires the name of the
            # species as input if not provided by the admin upon protocol
            # creation
            if "patho_typing" in nextflow_tag or "true_coverage" in nextflow_tag:
                processToParams[process_identifier]['species'] = config[
                    "CHEWBBACA_CORRESPONDENCE"][current_specie]

            if not os.path.exists(nexflow_user_dir):
                os.makedirs(nexflow_user_dir)

            array_of_files = []

            nextflow_resources = config["NEXTFLOW_RESOURCES"]

            # Additional parameters to change directives of assemblerflow
            additional_params = []

            for key, val in nextflow_resources[nextflow_tag].items():
                if key not in processToParams[process_identifier].keys():
                    if key == 'cpus' and cpus != '':
                        additional_params.append("'{}':'{}'".format(key, cpus))
                    elif key == 'memory' and memory != '':
                        memoryString = "\\\'{}GB\\\'".format(memory)
                        additional_params.append("'{}':'{}'".format(key, memoryString))
                    else:
                        additional_params.append("'{}':'{}'".format(key, val))

            # Add image directive if available
            if image != "":
                additional_params.append("'{}':'{}'".format("container", image))

            # Add or replace protocol params by the ones provided by the user
            for key, val in parameters.items():
                processToParams[process_identifier][key] = val

            # Add pid to parameters
            newProcessToParams = {}

            for key, val in processToParams[process_identifier].items():
                newProcessToParams['{}_{}'.format(key, process_id)] = val

            processToParams[process_identifier] = newProcessToParams

            # Add pid and additional parameters to flowcraft pipeline string
            assemblerflow_attr = "={{'pid':'{}',".format(process_id) + ","\
                .join(additional_params) + "}"

            # Merge all nextflow tags into an array
            nextflow_tags.append(nextflow_tag+assemblerflow_attr)

            # Case a process is the be run, ad it to the ids array to send to
            #  the frontend and change the status
            if process_to_run == "true":
                task_ids.append("project{}pipeline{}process{}"
                                .format(project_id, pipeline_id, process_id))

                processIDs.append(process_id)

            # Get the files to use as input if exist
            for x in files:
                array_of_files.append(
                    os.path.join(strain_submitter, config['FTP_FILES_FOLDER'],
                                 files[x]))

        # If no errors occur when getting the required variables, it writes
        # the platform.config file that is passed as input for nextflow and
        # runs flowcraft to build the pipeline and run it.
        if writeCacheFile:
            if os.path.exists(os.path.join(nexflow_user_dir,
                                           "platform.config")):
                os.remove(os.path.join(nexflow_user_dir,
                                       "platform.config"))
            to_write = {}

            # Create platform.config dictionary
            for identifier, params in processToParams.items():
                for param, value in params.items():
                    paramIdentifier = param
                    to_write[paramIdentifier] = value

            to_write["projectId"] = project_id
            to_write["pipelineId"] = pipeline_id
            to_write["platformHTTP"] = config["JOBS_ROOT_SET_OUTPUT"]
            to_write["sampleName"] = sampleName
            to_write["reportHTTP"] = config["JOBS_ROOT_SET_REPORT"]
            to_write["currentUserName"] = current_user_name
            to_write["currentUserId"] = current_user_id
            to_write["platformSpecies"] = current_specie

            # Object to write in the nexflow config
            '''to_write = {
                "asperaKey": asperaKey,
                "projectId": project_id,
                "pipelineId": pipeline_id,
                "platformHTTP": config["JOBS_ROOT_SET_OUTPUT"],
                "sampleName": sampleName,
                "reportHTTP": config["JOBS_ROOT_SET_REPORT"],
                "currentUserName": current_user_name,
                "currentUserId": current_user_id,
                "platformSpecies": current_specie,
                "genomeSize": config["species_expected_genome_size"][
                    current_specie],
                "schemaPath": chewbbaca_schema_path,
                "schemaSelectedLoci": chewbbaca_list_genes,
                "schemaCore": chewbbaca_core_genes_path,
                "chewbbacaTraining": chewbbaca_training_file,
                "chewbbacaJson": "true",
                "referenceFileO": seqtyping_ref_o,
                "referenceFileH": seqtyping_ref_h,
                "mlstSpecies": mlstSpecies,
                "species": "{}".format(specie)
            }
            '''

            # Case input is accessions, pass that argument to the
            # configuration file else, pass the fastq files path
            objKeys = to_write.keys()
            hasAccession = False

            for s in objKeys:
                if "accessions" in s:
                    hasAccession = True

            print hasAccession

            if not hasAccession:
                to_write["fastq"] = config["FASTQPATH"]
            else:
                to_write["accessions"] = accessionsPath


            with open(os.path.join(nexflow_user_dir, "platform.config"),
                      "w") as nextflow_cache_file:
                write_config_file(nextflow_cache_file, to_write)

            writeCacheFile = False

        # RUN FLOWCRAFT
        nextflow_file_location = os.path.join(nexflow_user_dir, random_pip_name)

        commands = ['python3', config["NEXTFLOW_GENERATOR_PATH"]] + ["build", "-t"] + \
                   [" ".join(nextflow_tags)] + \
                   ["-o", os.path.join(nexflow_user_dir,
                                       nextflow_file_location),
                    "-r", config["NEXTFLOW_GENERATOR_RECIPE"]]

        print commands

        proc = subprocess.Popen(commands, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        stdout, stderr = proc.communicate()

        # Parse for errors in the flowcraft build
        if stderr != "":
            return {'message': stderr}, 500

        # Write generator log
        with open(os.path.join(nexflow_user_dir, "nextflow_generator.log"),
                  "w") as next_gen_log:
            next_gen_log.write(" ".join(commands) + "\n")
            next_gen_log.write(stdout + "\n")

        # Write accessions
        if accessionsPath != "":
            with open(accessionsPath, "w") as accessions:
                accessions.write(json.loads(workflow['accession']) + "\t" + sampleName)

        # Remove previous nextflow log if exists
        try:
            log_location = os.path.join(os.path.join(homedir, "jobs", "{}-{}".format(
                job_parameters[0]['project_id'],
                job_parameters[0]['pipeline_id']
            )))
        except Exception as e:
            print e
            log_location = ""

        if os.path.isfile(os.path.join(log_location, ".nextflow.log")):
            os.remove(os.path.join(log_location, ".nextflow.log"))

        # RUN NEXTFLOW
        commands = ['sbatch',
                    os.path.abspath(
                        'job_processing/bash_scripts/nextflow_executor.sh'),
                    nexflow_user_dir, nextflow_file_location, array_of_files[0],
                    array_of_files[1], config["NEXTFLOW_PROFILE"], sampleName]

        print commands
        proc = subprocess.Popen(commands, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        stdout, stderr = proc.communicate()

        with open(os.path.join(nexflow_user_dir, "executor_command.txt"), "w")\
                as r:
            commands = commands[:4] + ['"{}"'.format(x) for x in commands[4:]]
            r.write(" ".join(commands))

        if stderr != "":
            return {'message': stderr}, 500

        return {'task_ids': task_ids, 'process_ids': processIDs}, 200

    def process_download_accessions(self, download_parameters):

        user_folder = '/home/users/' + download_parameters.username + '/' +\
                      config["FTP_FILES_FOLDER"]
        ena_file_txt = os.path.join(user_folder, 'ENA_file.txt')

        output_id = ''.join(
            random.choice(string.ascii_uppercase + string.digits)
            for _ in range(5))

        with open(ena_file_txt, 'w') as ena_file:
            ena_file.write('\n'.join(
                download_parameters.accession_numbers.split(",")) + '\n')

        f = open(os.path.join(user_folder, output_id + '_download.txt'), "w")

        # GETSEQ ENA PASSING FILES TO PREVIOUS DIR
        commands = 'python dependencies/getSeqENA/getSeqENA.py -l ' +\
                   ena_file_txt + ' -o ' + user_folder

        proc1 = subprocess.Popen(commands.split(' '), stdout=f)

        return {'output_file_id': output_id + '_download.txt'}, 200

    def insert_job(self, job_parameters, current_specie, sampleName,
                   current_user_name, current_user_id, homedir):
        # Insert jobs in queue
        jobID, code = self.process_job(job_parameters, current_specie,
                                       sampleName, current_user_name,
                                       current_user_id, homedir)
        return jobID, code

    def download_accessions(self, download_parameters):
        # Insert jobs in queue
        output, code = self.process_download_accessions(download_parameters)
        return output
