from rq import Queue #Queue
from redis import Redis
import subprocess
import os

#READ CONFIG FILE
config = {}
execfile("config.py", config)

redis_conn = Redis()
q = Queue('innuendo_jobs', connection=redis_conn)

class Queue_Processor:

	def process_job(self, **kwargs):
		key_value_args = []
		parameters = kwargs['parameters']['used Parameter']
		for key, value in parameters.iteritems():
			key_value_args.append(str(key))

			if str(key) == '-i':
				value += kwargs['username']
				key_value_args.append('-o')
				key_value_args.append('"' + str(value) + '"')
			
			elif len(value.split(' ')) > 1:
				key_value_args.append('"' + str(value) + '"')
			else:
				key_value_args.append(str(value))
			

		key_value_args.append("--spadesMaxMemory")
		key_value_args.append("4")

		#print key_value_args
		key_value_args = [config['INNUCA_PATH']] + key_value_args
		print key_value_args
		proc = subprocess.Popen(key_value_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		print proc.returncode
		if proc.returncode == 0:
			return True
		else:
			return False

	def insert_job(self, **kwargs):
		#Insert jobs in queue
		job = q.enqueue_call(func=self.process_job, kwargs=kwargs)