import os
import subprocess
from config import ADMIN_PASS

def create_user(username):
	os.putenv('INNUENDO_PASS', ADMIN_PASS)
	proc = subprocess.Popen(['create_user.sh', username], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	
	if proc.returncode != 0:
		print 'STDOUT'
		print stdout.decode("utf-8")
		print 'STDERR'
		print stderr.decode("utf-8")