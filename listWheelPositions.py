import os
import sys
import re

##
##  gets list of wheel index files from supplied directory
##  merges all into one list
## 

pathname=sys.argv[1]

try:
	myfiles = os.listdir(pathname)
except Exception as e:
	print("path {} raises exception {}".format(pathname,e))
	os._exit(-1)

pattern = "W_IDX"
newfilename=""
print("number of files found {}".format(len(myfiles)))
myfiles.sort()

idx=[]
fname=[]

for i in range(len(myfiles)):
	if re.match(pattern,myfiles[i]):
		newfilename=os.path.join(pathname,myfiles[i])
		with open(newfilename,mode='r') as f:
			fname.append(f.readline().strip())
			idx.append(int(f.readline().strip()))

newfilename=os.path.join(pathname,"wheel_IDX_list.csv")

with open(newfilename,mode='w') as f:
	for i in range(len(idx)):
		f.write("{},{}\n".format(fname[i],idx[i]))
		print("{}\t{}".format(fname[i],idx[i]))

os._exit(0)
