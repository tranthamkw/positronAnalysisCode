import os
import sys
import re
import glob
from os.path import exists
"""
Opens "masterSum.csv" in the directory of command line.

computes average <E>

computes average <D>

computes average <L>
"Usage:  python computeLDdiffernce <path-to-masterSum.csv> [y] chlo chhi

 y=scaling from chlo to chhi, empty or anything else, not scaled")

"""

sample=["D-Glucose II","L-Glucose II","Empty I","D-Glucose III","D-Glucose I","L-Glucose I","L-Glucose III","Empty II"]
# 0,1,2,3,4,5,6,7

max_bins=8192
max_idx=8
avgsugar=0.0
sugarlist=[0,1,3,4,5,6]  # position in the list above
Dlist=[0,3,4]
Llist=[1,5,6]

avgempty=0.0
emptylist=[2,7]

scaleFactor=[1.0 for x in range(max_idx)]
livetime=[0 for x in range(max_idx)]
sumcounts=[0 for x in range(max_idx)]
sHistogram=[[0 for x in range(max_bins)] for y in range(max_idx)]

EHistogram=[0.0 for x in range(max_bins)]
DHistogram=[0.0 for x in range(max_bins)]
LHistogram=[0.0 for x in range(max_bins)]


# reference histogram array data by
# mHistogram[idx][bin]


def calculateSums(lo,hi):
	global sHistogram
	global sumcounts
	global max_bins
	global max_idx
	if lo<10:
		lo=10
	if hi>max_bins:
		hi=max_bins
	for idx in range(max_idx):
		sumcounts[idx]=0
		for ch in range(lo,hi):
			sumcounts[idx]+=sHistogram[idx][ch]

def calculateAverages():
	global avgsugar
	global avgempty
	global sumcounts
	global sugarlist
	global emptylist

	tempsum=0.0
	for i in range(len(sugarlist)):
		tempsum+=float(sumcounts[sugarlist[i]])
	avgsugar = tempsum/float(len(sugarlist))

	tempsum=0.0
	for i in range(len(emptylist)):
		tempsum+=float(sumcounts[emptylist[i]])
	avgempty = tempsum/float(len(emptylist))

def calculateScaleFactor(lo,hi):
	global sugarlist
	global emptylist
	global scaleFactor

	calculateSums(lo,hi)
	calculateAverages()
	for i in range(len(sugarlist)):
		scaleFactor[sugarlist[i]]=avgsugar/float(sumcounts[sugarlist[i]])
	for i in range(len(emptylist)):
		scaleFactor[emptylist[i]]=avgempty/float(sumcounts[emptylist[i]])

def scaleAndAverage():
	global emptylist
	global Dlist
	global Llist
	global scaleFactor
	global sHistogram
	global EHistogram
	global LHistogram
	global DHistogram
	global max_bins

	for ch in range(max_bins):
		DHistogram[ch]=0.0
		for i in range(len(Dlist)):
			DHistogram[ch]+=scaleFactor[Dlist[i]]*float(sHistogram[Dlist[i]][ch])
		DHistogram[ch]=DHistogram[ch]/float(len(Dlist))

		LHistogram[ch]=0.0
		for i in range(len(Llist)):
			LHistogram[ch]+=scaleFactor[Llist[i]]*float(sHistogram[Llist[i]][ch])
		LHistogram[ch]=LHistogram[ch]/float(len(Llist))

		EHistogram[ch]=0.0
		for i in range(len(emptylist)):
			EHistogram[ch]+=scaleFactor[emptylist[i]]*float(sHistogram[emptylist[i]][ch])
		EHistogram[ch]=EHistogram[ch]/float(len(emptylist))
"""
def smoothHistograms(pts):
	global sHistogram
	global EHistogram
	global LHistogram
	global DHistogram
	global max_bins

	temphistogram=[0.0 for x in range(max_bins)]
	for ch in range(pts,max_bins-pts-2):
		for i in range(1,pts+1):
			temphistogram[ch]+=(EHistogram[ch-i]+EHistogram[ch+i])
		temphistogram[ch]=temphistogram[ch]/float(pts
"""

################### START MAIN



chlo = 350
chhi = max_bins
scale = False
allgood=True

argc=len(sys.argv)

pathname=re.sub("/","",sys.argv[1])

if argc==2:
	filename = pathname+"/masterSum.csv"
	if not exists(filename):
		print("{}  not found".format(filename))
		os._exit(-1)
elif (argc==5) and (re.search("y",sys.argv[2])):
	filename = pathname+"/masterSum.csv"
	if not exists(filename):
		print("{}  not found".format(filename))
		os._exit(-1)
	scale = True
	chlo = int(sys.argv[3])
	chhi = int(sys.argv[4])
else:
	print("Usage:  python computeLDdiffernce <path-to-masterSum.csv> [y] chlo chhi \n y=scaling from chlo to chhi, empty or anything else, not scaled")
	os._exit(-1)
#TODO put in error traping for lo and hi

print(filename)
print(scale)
print("lo {}\thi {}".format(chlo,chhi))


#open the file 
with (open(filename,mode='r')) as f:
	headerline=f.readline() #this contains the files used as input to the process
	line=f.readline() # this is the index line. dispose of this
	line=f.readline() # line 3 has sample ID's.  we will check to see if they match the expected order.
	allgood=True
	linelist=line.split(",")
	if len(linelist)==(max_idx+1):
		for j in range(max_idx):
			allgood=allgood and bool(re.match(sample[j],linelist[j+1]))
		if not allgood:
			print("line 3 does sample list does not match expected")
			os._exit(-1)
	else:
		print("unexpected length on line 3")
		os._exit(-1)

	line = f.readline() #line 4 has livetime for each sample
	linelist=line.split(",")
	if len(linelist)==(max_idx+1):
		for j in range(max_idx):
			livetime[j]=int(linelist[j+1])
	else:
		print("unexpected length on line 4")
		os._exit(-1)

#TODO check that all livetimes are the same

	line = f.readline() # line 5 is a simple header. ignore
	ch=0
	line = f.readline()
	while (line and ch < max_bins):
		linelist=line.split(",")
		if ((ch==int(linelist[0])) and (len(linelist)==max_idx+1)):
			for idx in range(max_idx):
				sHistogram[idx][ch]+=int(linelist[idx+1])
		else:
			print("unexpected entry first column, row {}".format(ch))
			print("or line length unexpected: {}".format(len(linelist)))
			print(linelist)
			os._exit(-1)
		ch+=1
		line=f.readline()
# compute averages and stuff

# compute sum counts for scaling
if scale:
	calculateScaleFactor(chlo,chhi)
else:
	for i in range(max_idx):
		scaleFactor[i]=1.0

print("Scale factors by sample location")
for i in range(max_idx):
	print("{}\t{}\t{}".format(i,sample[i],scaleFactor[i]))

scaleAndAverage()


# save master sum

final_filename=pathname+"/EDL_Histogram"+re.sub("/","",sys.argv[1])+".csv"
print("summed to {}".format(final_filename))
with open(final_filename,mode='w') as f:
	f.write(headerline)
	f.write("\n")
	f.write("LiveTime,{}\n".format(livetime[1]))
	f.write("Channel range for scaling,{},{}\n".format(chlo,chhi))
	f.write("Scaling enabled,{}\n".format(scale))
	f.write("Scale factors by sample location\n")
	for i in range(max_idx):
		f.write("{},{},{}\n".format(i,sample[i],scaleFactor[i]))
	f.write("Ch,E,D,L\n")
	for j in range(max_bins):
		f.write("{},{},{},{}\n".format(j,EHistogram[j],DHistogram[j],LHistogram[j]))

#newfilename=os.path.join(pathname,"wheel_IDX_list.csv")

print("\nDone")
os._exit(0)
