import os
import subprocess
import config
import random
import string

def create_user(username, upload_folder):
	os.putenv('INNUENDO_PASS', config.ADMIN_PASS)
	proc = subprocess.Popen(['sh', os.path.join(os.getcwd(),'app/utils/create_user.sh'), username, upload_folder], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = proc.communicate()

def random_letters(n):
	return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(n))