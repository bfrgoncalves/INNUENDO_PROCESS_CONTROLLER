import json
import os
from glob import glob

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

	key_value_args.append('--json')

	config = {}
	execfile("config.py", config)

	config['FILETYPES_SOFTWARE']['INNUca'][0]['app_path']

	#after_application_steps = '; python ' + config['FILETYPES_SOFTWARE']['INNUca'][0]['app_path'] + 'combine_reports.py -i ' + os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID')
	after_application_steps = '; mkdir ' + os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID') + '/INNUca_SLURM_ARRAY_JOB_ID_$SLURM_ARRAY_TASK_ID;'
	#after_application_steps += ' ln -s $(cat ' + os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID') + '/final_assembly.txt) ' + os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/INNUca;' 
	after_application_steps += ' ln -s ' + os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID') + '/samples_report.*.json ' + os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/INNUca_SLURM_ARRAY_JOB_ID_$SLURM_ARRAY_TASK_ID/run_info.json;' 
	after_application_steps += ' ln -s ' + os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID') + '/combine_samples_reports.*.json ' + os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/INNUca_SLURM_ARRAY_JOB_ID_$SLURM_ARRAY_TASK_ID/run_stats.json;' 

	#MOVE ASSEMBly to job folder
	after_application_steps += ' ln -s $(cat '+os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID')+'*/final_assembly.txt) '+ os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/INNUca_SLURM_ARRAY_JOB_ID_$SLURM_ARRAY_TASK_ID/run_output.fasta;' 

	
	'''for file_found in glob(os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID')+'/*/final_assembly.txt'):
		print 'AQUI!!'
		with open(file_found,'r') as ff:
			line = ff.next()
			after_application_steps += ' ln -s ' + line +' '+ os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/INNUca_SLURM_ARRAY_JOB_ID_$SLURM_ARRAY_TASK_ID/run_output.json;' 
	'''
	print after_application_steps
	return key_value_args, prev_application_steps, after_application_steps


def process_chewbbaca(key_value_args, parameters, user_folder):
	#list of genomes
	#list of genes

	#READ CONFIG FILE
	config = {}
	execfile("config.py", config)

	prev_application_steps = 'find ' + user_folder + '/SLURM_ARRAY_JOB_ID/*/*.fasta > ' + user_folder + '/SLURM_ARRAY_JOB_ID/listGenomes.txt; '
	prev_application_steps += 'find ' + 'dependencies/chewBBACA/campy_scheme_2017/genes/*.fasta > ' + user_folder + '/SLURM_ARRAY_JOB_ID/listGenes.txt;'
	prev_application_steps += 'mkdir ' + os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID') + '/chewBBACA_SLURM_ARRAY_JOB_ID_$SLURM_ARRAY_TASK_ID; '

	key_value_args.append('-i')
	key_value_args.append(os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID', 'listGenomes.txt'))

	key_value_args.append('-o')
	key_value_args.append(os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID/chewBBACA_SLURM_ARRAY_JOB_ID_$SLURM_ARRAY_TASK_ID'))

	key_value_args.append('-b')
	key_value_args.append(config['BLAST_PATH'])

	key_value_args.append('-g')
	key_value_args.append(os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID','listGenes.txt'))

	key_value_args.append('--cpu')
	key_value_args.append('3')

	key_value_args.append('--json')

	after_application_steps = ''

	#MOVE RESULTS to job folder
	for directory_found in glob(os.path.join(str(user_folder),'SLURM_ARRAY_JOB_ID/chewBBACA_SLURM_ARRAY_JOB_ID_$SLURM_ARRAY_TASK_ID')+'/*'):
		for file_found in glob(directory_found):
			txt_name = ""
			if "Status" in file_found:
				txt_name = "run_info.json"
			elif "alleles" in file_found:
				txt_name = "run_output.json"
			elif "statistics" in file_found:
				txt_name = "run_stats.json"
			
			after_application_steps += ' ln -s ' + file_found +' '+ os.path.join(str(user_folder),"SLURM_ARRAY_JOB_ID") + '/chewBBACA_SLURM_ARRAY_JOB_ID_$SLURM_ARRAY_TASK_ID/'+txt_name+';'
		
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