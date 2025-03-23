import os
import sys
import re
import glob
from os.path import exists

sample=["D-Glucose II","L-Glucose II","Empty I","D-Glucose III","D-Glucose I","L-Glucose I","L-Glucose III","Empty II"]

myfiles=[]
#filelist=[]



"""
program opens "regionSums.csv" in every directory passed in the commandline
and combines/appends into one master file...
the list is sorted.  It also computes hour based on input filename. the first directory is taken
as hour 0-23, the second directory is 24-47, etc. 

writes to "masterSum.csv" in the last directory of the list.

Usage:
python masterRegionalSums <sub-directory> <sub-directory> . . . as many subdirectories as needed.

if "/" is missing from the end-string of the sub-directory, it is automatically appended.

e.g.
python masterRegionalSums.py 3-5-25 3-4-25

"""

infilename=[]
timeidx=[]
temperature=[]
livetime=[]
mylist=[]

allgood=True

argc=len(sys.argv)
print("argc {}".format(argc))

pathlist=[]

for i in range(1,argc):
	pathlist.append(re.sub("/","",sys.argv[i]))

pathlist.sort()

pathname=pathlist[len(pathlist)-1]

for i in range(len(pathlist)):
	filename = pathlist[i]+"/regionSums.csv"
	allgood = allgood and exists(filename)
	if allgood:
		myfiles.append(filename)
	else:
		print("{}  not found".format(filename))
		os._exit(-1)


regions=[]

for i in range(len(myfiles)):  #open each file and channel by channel sum histograms
	with (open(myfiles[i],mode='r')) as f:
		line=f.readline()
		line=re.sub(r"\n","",line)
		linelist=line.split(",")
		if i==0:
			numregions=int(linelist[len(linelist)-1])-1
			print("num regions {}".format(numregions))
		else:
			if not (numregions==int(linelist[len(linelist)-1])-1):
				print("inconsistent number of regions")
				exit(-1)
		line=f.readline() #filename and other header
		line=f.readline() #first line with real data
		line=re.sub(r"\n","",line)
		linelist=line.split(",")
#		print("len linelist {}\t regions {}".format(len(linelist),numregions))
		while len(linelist)==(4+numregions):
			temp=linelist[0]
			regions=[0 for y in range(numregions)]
			infilename.append(linelist[0])
			result = re.search("_",temp)
			j=result.start()
			substr1=temp[j+1:j+3]
			substr2=temp[j+3:j+5]
			timeidx.append(i*24.0+float(substr1)+float(substr2)/60.0)
#			print("timeidx {}".format(i*24.0+float(substr1)+float(substr2)/60.0))
			temperature.append(linelist[1])
			livetime.append(linelist[2])
			for k in range(numregions):
				regions[k]=int(linelist[3+k])

		#	print(regions)
			mylist.append(regions)

			line=f.readline()
			line=re.sub(r"\n","",line)
			linelist=line.split(",")

# save master region

"""
for x in mylist:
	for y in x:
		print(y,end=" ")
	print()

exit(0)
"""

#print("All good {}".format(allgood))
final_filename=pathname+"/masterRegionalSum"+pathname+".csv"

print("Aggregate to {}".format(final_filename))

with open(final_filename,mode='w') as f:
	f.write("Infile,time(hr),temperature,livetime, regions\n")
	for i in range(len(infilename)):
		f.write("{},".format(infilename[i]))
		f.write("{},".format(timeidx[i]))
		f.write("{},".format(temperature[i]))
		f.write("{},".format(livetime[i]))
		for k in range(numregions):
			f.write("{},".format(mylist[i][k]))
		f.write("\n")


print("\nDone")
os._exit(0)
