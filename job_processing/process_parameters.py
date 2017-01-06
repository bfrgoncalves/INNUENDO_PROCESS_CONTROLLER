import json
import os

def get_protocol_parameters(parameters):

	key_value_args = []

	for key, value in parameters.iteritems():
		if key == '-i' or key == '-o':
			continue
		else:
			key_value_args.append(str(key))

			if len(value.split(' ')) > 1:
				key_value_args.append("'" + str(value) + "'")
			else:
				key_value_args.append(str(value))

	return key_value_args


def process_innuca(key_value_args, parameters, user_folder):

	prev_application_steps = ''

	key_value_args.append('-i')
	key_value_args.append(os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID'))

	key_value_args.append('-o')
	key_value_args.append(os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID'))

	after_application_steps = '; mkdir ' + os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID') + '/INNUca; '
	after_application_steps += '; ln -s $(cat ' + os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID') + '/*/final_assembly.txt) ' + os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/innuca_assembly_SLURM_ARRAY_JOB_ID.fasta;' 

	#after_application_steps = 'count_assemblies=0; for file_found in $(find . -name final_assembly.txt); do (( count_assemblies++ )); ln -s $(cat $file_found) '+os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID")+'/innuca_assembly_SLURM_ARRAY_JOB_ID.fasta; done'

	#MOVE ASSEMBly to job folder

	return key_value_args, prev_application_steps, after_application_steps


def process_chewbbaca(key_value_args, parameters, user_folder):
	#list of genomes
	#list of genes

	#READ CONFIG FILE
	config = {}
	execfile("config.py", config)

	prev_application_steps = 'find ' + user_folder + '/SLURM_ARRAY_JOB_ID/*.fasta > ' + user_folder + '/SLURM_ARRAY_JOB_ID/listGenomes.txt; '
	prev_application_steps += 'find ' + user_folder + '/AgalSchema/*.fasta > ' + user_folder + '/SLURM_ARRAY_JOB_ID/listGenes.txt;'

	key_value_args.append('-i')
	key_value_args.append(os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID', 'listGenomes.txt'))

	key_value_args.append('-o')
	key_value_args.append(os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID/'))

	key_value_args.append('-b')
	key_value_args.append(config['BLAST_PATH'])

	key_value_args.append('-g')
	key_value_args.append(os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID','listGenes.txt'))

	after_application_steps = '; mkdir ' + os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID') + '/chewBBACA; '

	return key_value_args, prev_application_steps, after_application_steps
	


def process_parameters(parameters, user_folder, workflow):

	#READ CONFIG FILE
	config = {}
	execfile("config.py", config)

	options = {'INNUca':process_innuca, 'chewBBACA':process_chewbbaca}

	wf_params = json.loads(workflow['parameters'])
	if wf_params['used Software'] in config['APPLICATIONS_ARRAY']:
		software = wf_params['used Software']

	options = {'INNUca':process_innuca, 'chewBBACA':process_chewbbaca}

	key_value_args = get_protocol_parameters(parameters)
	key_value_args, prev_application_steps, after_application_steps = options[software](key_value_args, parameters, user_folder)


	return key_value_args, prev_application_steps, after_application_steps