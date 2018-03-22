from rq import Queue
from redis import Redis
import subprocess
import os
import json
import string
import random

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
        file_instance.write('{}:"{}"\n'.format(key, val))

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

        # To send to nextflow generator
        project_id = ""
        pipeline_id = ""
        nexflow_user_dir = ""
        chewbbaca_schema_path = ""
        chewbbaca_list_genes = ""
        chewbbaca_core_genes_path = ""
        chewbbaca_species = ""
        seqtyping_ref_o = ""
        seqtyping_ref_h = ""
        patho_species = ""
        mlstSpecies = ""

        random_pip_name = job_parameters[0]['project_id']+'_'+ \
                          job_parameters[0]['pipeline_id']+ ".nf"

        for workflow in job_parameters:

            count_workflows += 1
            parameters = json.loads(workflow['parameters'])['used Parameter']
            files = json.loads(workflow['files'])
            # username = workflow['username']
            strain_submitter = workflow['strain_submitter']
            # workflow_name = json.loads(workflow['parameters'])['name']
            used_software = json.loads(workflow['parameters'])['used Software']
            nextflow_tag = json.loads(workflow['parameters'])['Nextflow Tag']
            project_id = workflow['project_id']
            pipeline_id = workflow['pipeline_id']
            process_id = workflow['process_id']
            process_to_run = workflow['process_to_run']

            nexflow_user_dir = os.path.join(homedir, "jobs", project_id+"-"+
                                            pipeline_id)

            if "chewBBACA" in used_software and process_to_run == "false":
                continue

            if "mlst" in used_software:
                mlstSpecies = config["MLST_CORRESPONDENCE"][current_specie]

            if "chewBBACA" in used_software:
                chewbbaca_species = config["CHEWBBACA_CORRESPONDENCE"][
                    current_specie]
                chewbbaca_schema_path = os.path.join(
                    config["CHEWBBACA_SCHEMAS_PATH"], parameters["schema"])
                chewbbaca_list_genes = os.path.join(
                    config["CHEWBBACA_SCHEMAS_PATH"], parameters["schema"],
                    "listGenes.txt")
                chewbbaca_core_genes_path = config[
                    "core_headers_correspondece"][current_specie]

            if "seq_typing" in used_software:
                seqtyping_ref_o = config["SEQ_FILE_O"][current_specie]
                seqtyping_ref_h = config["SEQ_FILE_H"][current_specie]

            if "patho_typing" in used_software:
                patho_species = config["CHEWBBACA_CORRESPONDENCE"][
                    current_specie]

            if not os.path.exists(nexflow_user_dir):
                os.makedirs(nexflow_user_dir)

            array_of_files = []

            nextflow_tags.append(nextflow_tag+":"+process_id)

            if process_to_run == "true":
                task_ids.append("project{}pipeline{}process{}"
                                .format(project_id, pipeline_id, process_id))

                processIDs.append(process_id)

            for x in files:
                array_of_files.append(
                    os.path.join(strain_submitter, config['FTP_FILES_FOLDER'],
                                 files[x]))

        if writeCacheFile:
            if os.path.exists(os.path.join(nexflow_user_dir,
                                           "platform.config")):
                os.remove(os.path.join(nexflow_user_dir,
                                       "platform.config"))

            # Object to write in the nexflow config
            to_write = {
                "--projectId": project_id,
                "--pipelineId": pipeline_id,
                "--platformHTTP": config["JOBS_ROOT_SET_OUTPUT"],
                "--sampleName": sampleName,
                "--reportHTTP": config["JOBS_ROOT_SET_REPORT"],
                "--currentUserName": current_user_name,
                "--currentUserId": current_user_id,
                "--species": current_specie,
                "--genomeSize": config["species_expected_genome_size"][
                    current_specie],
                "--schemaPath": chewbbaca_schema_path,
                "--schemaSelectedLoci": chewbbaca_list_genes,
                "--schemaCore": chewbbaca_core_genes_path,
                "--chewbbacaSpecies":"{}".format(chewbbaca_species),
                "--referenceFileO": seqtyping_ref_o,
                "--referenceFileH": seqtyping_ref_h,
                "--pathoSpecies": patho_species

            }

            with open(os.path.join(nexflow_user_dir, "platform.config"),
                      "w") as nextflow_cache_file:
                write_config_file(nextflow_cache_file, to_write)

            writeCacheFile = False

        # RUN Nextflow GENERATOR
        nextflow_file_location = os.path.join(nexflow_user_dir, random_pip_name)

        commands = ['python3', config["NEXTFLOW_GENERATOR_PATH"]] + ["-t"] + \
                   nextflow_tags + ["-o", os.path.join(nexflow_user_dir,
                                                       nextflow_file_location),
                                    "--include-templates"]

        print commands

        proc = subprocess.Popen(commands, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        stdout, stderr = proc.communicate()

        if stderr != "":
            return {'message': stderr}, 500

        with open(os.path.join(nexflow_user_dir, "nextflow_generator.log"),
                  "w") as next_gen_log:
            next_gen_log.write(" ".join(commands) + "\n")
            next_gen_log.write(stdout + "\n")


        # RUN NEXTFLOW
        commands = ['sbatch',
                    os.path.abspath(
                        'job_processing/bash_scripts/nextflow_executor.sh'),
                    nexflow_user_dir, nextflow_file_location, array_of_files[0],
                    array_of_files[1], config["NEXTFLOW_PROFILE"]]

        print commands
        proc = subprocess.Popen(commands, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()

        with open(os.path.join(nexflow_user_dir, "executor_command.txt"), "w")\
                as r:
            commands = commands[:4] + ['"{}"'.format(x) for x in commands[4:]]
            r.write(" ".join(commands))

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
        return jobID

    def download_accessions(self, download_parameters):
        # Insert jobs in queue
        output, code = self.process_download_accessions(download_parameters)
        return output
