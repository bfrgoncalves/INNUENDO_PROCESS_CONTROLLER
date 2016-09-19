import os
import subprocess
import config

def create_user(username):
	os.putenv('INNUENDO_PASS', config.ADMIN_PASS)
	print config.ADMIN_PASS
	print os.path.join(os.getcwd(),'app/utils/create_user.sh')
	proc = subprocess.Popen(['sh', os.path.join(os.getcwd(),'app/utils/create_user.sh'), username], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	print config.ADMIN_PASS
	if proc.returncode != 0:
		print 'STDOUT'
		print stdout.decode("utf-8")
		print 'STDERR'
		print stderr.decode("utf-8")