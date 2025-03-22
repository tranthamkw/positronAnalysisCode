import os
import sys
import re


from sumRegions import(sumH)

""" this is the channel numbers which serve to divide the regions """

regions=[350,2400,3600,6200,8000]

""" use as many as needed.  e.g. with regions=[15,300,600] the program
will sum:
region[0] = sum from channels 15 to 299
region[1] = sum from channels 300 to 699
"""


pathname=sys.argv[1]

try:
	myfiles = os.listdir(pathname)
except Exception as e:
	print("path {} raises exception {}".format(pathname,e))
	os._exit(-1)

pattern = "^GSPEC"
newfilename=""
print(len(myfiles))
myfiles.sort()
outfilename=os.path.join(pathname,"regionSums.csv")

with open(outfilename,mode='w') as f:
	f.write("Regions used,")
	for i in range(len(regions)):
		f.write("{},".format(regions[i]))
	f.write("{}\n".format(len(regions)))

	f.write("Filename of histogram,Temperature of PMT,Livetime,")

	for i in range(len(regions)-1):
		f.write("ch {} to {},".format(regions[i],regions[i+1]))
	f.write("\n")
	for i in range(len(myfiles)):
		if re.match(pattern,myfiles[i]):
			newfilename=os.path.join(pathname,myfiles[i])
			tmpstr=sumH(newfilename,regions)
			f.write(tmpstr)
			tmpstr=re.sub(r"\n","",tmpstr)
			print(tmpstr)


os._exit(0)
