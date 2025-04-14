import os
import sys
import re
import glob
import argparse

from sumRegions import(sumH)

""" this is the channel numbers which serve to divide the regions """

regions=[1000,2400,3600,6200,8000]

""" use as many as needed.  e.g. with regions=[15,300,600] the program
will sum:
region[0] = sum from channels 15 to 299
region[1] = sum from channels 300 to 699
"""

parser = argparse.ArgumentParser(
        prog='processRegionSum',
        description='Sums over channels in regions specified by list regions',
        epilog="e.g. python processRegionSums.py <directory>")
parser.add_argument('directory',type=str,help='directory')


args = parser.parse_args()
pathname=args.directory

# if a slash was passed, remove it.  add one at the end. this
# essentially adds a slash if we forget to add it.

pathname=re.sub("/","",pathname)
pathname+="/"

try:
	myfiles = glob.glob(pathname+"GSPEC*.csv")
# returns a list that looks like '3-17-25/GSPEC2025-03-17_200001.csv'
#	myfiles = os.listdir(pathname)
except Exception as e:
	print("path {} raises exception {}".format(pathname,e))
	os._exit(-1)

pattern = "^GSPEC"
newfilename=""
print(len(myfiles))

for i in range(len(myfiles)):
	myfiles[i]=re.sub(pathname,"",myfiles[i])

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
		if re.match(pattern,myfiles[i]): #if match pattern prolly not needed with glob statement
			newfilename=os.path.join(pathname,myfiles[i])
			tmpstr=sumH(newfilename,regions)
			f.write(tmpstr)
			tmpstr=re.sub(r"\n","",tmpstr)
			print(tmpstr)

os._exit(0)
