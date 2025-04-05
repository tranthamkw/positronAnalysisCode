import os
import sys
import re
import glob
from os.path import exists
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


sample=["D-Glucose II","L-Glucose II","Empty I","D-Glucose III","D-Glucose I","L-Glucose I","L-Glucose III","Empty II"]

myfiles=[]

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

myday=0
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
			substr3=temp[j-2:j]
			if i==0:
				myday=float(substr3)
				day=0
			else:
				day=float(substr3)-myday

			timeidx.append(day*24.0+float(substr1)+float(substr2)/60.0)
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



fig=plt.figure()
# Set global font sizes using rcParams
plt.rcParams.update({
    'font.size': 12,           # General text size
    'xtick.labelsize': 10,      # X-axis tick labels
    'ytick.labelsize': 10,      # Y-axis tick labels
    'axes.labelsize': 12,       # X and Y labels
    'axes.titlesize': 12,       # Title size
    'legend.fontsize': 10,       # Legend font size
    'figure.figsize': (10,7),   # Figure size
    'errorbar.capsize': 3,      # Errorbar capsize
    'lines.markersize': 6,        # Marker size
})

#fig.set_size_inches(7, 5)

plt.plot(timeidx,temperature,marker='o',ms=3,mec = 'DarkRed', mfc = 'DarkRed',ls='')
plt.xlabel("Hour")
plt.ylabel("Temperature (C)")
plt.title("Temperature (C)")
#plt.ylim(0, 30)
bottom,top=plt.ylim()
plt.ylim(-1,2)
print("{}\t{}".format(bottom,top))
plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(12))
plt.gca().xaxis.set_minor_locator(ticker.MultipleLocator(4))
plt.grid(color = 'DodgerBlue', linestyle = '--', linewidth = 0.5)
fig.savefig(os.path.join(pathname,"graphTemperature.png"))

mycolors=['DarkOrange','DarkOrchid','DarkSlateBlue','ForestGreen']


plt.clf()

for k in range(numregions):
	tmparray=[0 for x in range(len(timeidx))]
	for i in range(len(timeidx)):
		tmparray[i]=mylist[i][k]
	plt.plot(timeidx,tmparray,marker='o',ms=3,mec = mycolors[k%4], mfc = mycolors[k%4],ls='')

mylegend=[]
plt.xlabel("Hour")
plt.ylabel("Total counts/livetime")
plt.title("Regional Sums")
for k in range(numregions):
	mylegend.append("Region {}".format(k))

plt.legend(mylegend, loc='lower right')
plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(24))
plt.gca().xaxis.set_minor_locator(ticker.MultipleLocator(4))
plt.grid(color = 'DodgerBlue', linestyle = '--', linewidth = 0.5)
fig.savefig(os.path.join(pathname,"graphRegions.png"),dpi=300)

print("Done")
os._exit(0)
