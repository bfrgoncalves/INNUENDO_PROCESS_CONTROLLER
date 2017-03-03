#CONFIG file for INNUENDO Job Controller
REDIS_URL = 'redis://localhost:6379'

#Folder for files with jobs
JOBS_FOLDER = 'job_processing/parameters_files'

#BLAST PATH
BLAST_PATH = '/home/innuendo/sandbox/ncbi-blast-2.5.0+/bin/blastp'

#Available applications
APPLICATIONS_ARRAY = ['INNUca', 'chewBBACA', '']
FILETYPES_SOFTWARE = {'INNUca': [{'language':'python', '-f': '.fastq', 'app_path': 'dependencies/INNUca/', 'path': 'dependencies/INNUca/INNUca.py'}], 'chewBBACA':[{'language': 'python', '-f': 'fasta', 'app_path': 'dependencies/chewBBACA/', 'path': 'dependencies/chewBBACA/allelecall/BBACA.py'}]}