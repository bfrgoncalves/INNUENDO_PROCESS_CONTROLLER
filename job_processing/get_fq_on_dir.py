import os
import glob
import sys

file_names = ""
file1 = ""
file2 = ""

print sys.argv[1]
for f in glob.glob(os.path.join(sys.argv[0],"*q.gz")):
	print f
	if "_R1_" in f or "_1." in f:
		file1 = f
	elif "_R2_" in f or "_2." in f:
		file2 = f

sys.stdout.write(file1 + " " + file2)
