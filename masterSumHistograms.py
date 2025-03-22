import os
import sys
import re
import glob
from os.path import exists

sample=["D-Glucose II","L-Glucose II","Empty I","D-Glucose III","D-Glucose I","L-Glucose I","L-Glucose III","Empty II"]

max_bins=8192
max_idx=8
myfiles=[]
filelist=[]
livetime=[0 for x in range(max_idx)]
sHistogram=[[0 for x in range(max_bins)] for y in range(max_idx)]
# reference histogram array data by
# mHistogram[idx][bin]


"""
program opens "SortedAndSummedHistograms.csv" in every directory passed in the commandline
and channel-by-channel sums the histograms for each, individual sample ID.  Also sums
total live time for each sample ID

writes to "masterSum.csv" in the last directory of the list.

Usage:
python masterSumHistograms <sub-directory> <sub-directory> . . . as many subdirectories as needed.

if "/" is missing from the end-string of the sub-directory, it is automatically appended.

e.g.
python masterSumHistograms 2-28-25 3-1-25

"""



allgood=True

argc=len(sys.argv)

for i in range(1,argc):
	if re.search("$/",sys.argv[i]):
		filename = sys.argv[i]+"SortedAndSummedHistgrams.csv"
	else:
		filename = sys.argv[i]+"/SortedAndSummedHistgrams.csv"
	allgood = allgood and exists(filename)
	if allgood:
		myfiles.append(filename)
	else:
		print("{}  not found".format(filename))
		os._exit(-1)

for i in range(len(myfiles)):  #open each file and channel by channel sum histograms
	with (open(myfiles[i],mode='r')) as f:
		filelist.append(f.readline())
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
				livetime[j]+=int(linelist[j+1])
		else:
			print("unexpected length on line 4")
			os._exit(-1)

		line = f.readline() # line 5 is a simple header. ignore

		ch=0
		line = f.readline()
		while (line and ch < max_bins):
			linelist=line.split(",")
			if ((ch==int(linelist[0])) and (len(linelist)==max_idx+1)):
				for idx in range(max_idx):
#					print("idx {}\tch {}".format(idx,ch))
					sHistogram[idx][ch]+=int(linelist[idx+1])
			else:
				print("unexpected entry first column, row {}".format(ch))
				print("or line length unexpected: {}".format(len(linelist)))
				print(linelist)
				os._exit(-1)
			ch+=1
			line=f.readline()



# save master sum

if re.search("$/",sys.argv[argc-1]):
	final_filename=sys.argv[argc-1]+"masterSum.csv"
else:
	final_filename=sys.argv[argc-1]+"/masterSum.csv"


print("summed to {}".format(final_filename))
with open(final_filename,mode='w') as f:
	f.write("files used:")
	for i in range(len(myfiles)):
		f.write(",{}".format(myfiles[i]))
	f.write("\n")
	f.write("Sample Index")
	for i in range(max_idx):
		f.write(",{}".format(i))
	f.write("\n")
	f.write("Sample")
	for i in range(max_idx):
		f.write(",{}".format(sample[i]))
	f.write("\n")
	f.write("LiveTime")
	for i in range(max_idx):
		f.write(",{}".format(livetime[i]))
	f.write("\n")
	f.write("Ch")
	for i in range(max_idx):
		f.write(",data")
	f.write("\n")
	for j in range(max_bins):
		f.write("{}".format(j))
		for i in range(max_idx):
			f.write(",{}".format(sHistogram[i][j]))
		f.write("\n")


#newfilename=os.path.join(pathname,"wheel_IDX_list.csv")

print("\nDone")
os._exit(0)
