import os
import subprocess
from config import ADMIN_PASS

def create_user(username):
	os.putenv('INNUENDO_PASS', ADMIN_PASS)
	subprocess.call('create_user.sh', shell=True)