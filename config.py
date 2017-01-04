#CONFIG file for INNUENDO Job Controller
REDIS_URL = 'redis://localhost:6379'

#Available applications
APPLICATIONS_ARRAY = ['INNUca']
FILETYPES_SOFTWARE = {'INNUca': [{'language':'python', '-f': '.fastq', 'path': 'dependencies/INNUca/INNUca.py'}]}
