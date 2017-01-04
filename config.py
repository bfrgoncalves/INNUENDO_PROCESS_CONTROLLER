#CONFIG file for INNUENDO Job Controller
REDIS_URL = 'redis://localhost:6379'

#Folder for files with jobs
JOBS_FOLDER = 'job_processing/parameters_files'
#Available applications
APPLICATIONS_ARRAY = ['INNUca', '']
FILETYPES_SOFTWARE = {'INNUca': [{'language':'python', '-f': '.fastq', 'path': 'dependencies/INNUca/INNUca.py'}]}
