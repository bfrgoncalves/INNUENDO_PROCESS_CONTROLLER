import os
import subprocess
import config
import random
import string

def random_letters(n):
	return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(n))

def create_user(username, upload_folder):
	os.putenv('INNUENDO_PASS', config.ADMIN_PASS)
	passw = random_letters(7)
	proc = subprocess.Popen(['sh', os.path.join(os.getcwd(),'app/utils/create_user.sh'), username, upload_folder, passw], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = proc.communicate()

	if proc.returncode != 0:
		print 'STDOUT'
		print stdout.decode("utf-8")
		print 'STDERR'
		print stderr.decode("utf-8")

	return passw

def changepass(username):
	os.putenv('INNUENDO_PASS', config.ADMIN_PASS)
	passw = random_letters(7)
	proc = subprocess.Popen(['sh', os.path.join(os.getcwd(),'app/utils/changepass.sh'), username, passw], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	
	stdout, stderr = proc.communicate()
	if proc.returncode != 0:
		print 'STDOUT'
		print stdout.decode("utf-8")
		print 'STDERR'
		print stderr.decode("utf-8")

	return passw
