import os
import sys
import re
import glob
import argparse

sample=["D-Glucose II","L-Glucose II","Empty I","D-Glucose III","D-Glucose I","L-Glucose I","L-Glucose III","Empty II"]

max_bins=8192
max_idx=8

livetime=[0 for x in range(max_idx)]
mHistogram=[[0 for x in range(max_bins)] for y in range(max_idx)]
# reference histogram date by
# mHistogram[idx][bin]

def areSame(pre1,text1,pre2,text2):
	result=re.search(pre1,text1)
#	text1=re.sub("^"+pre1,"",text1)
	i=result.start()
	text1=text1[i+5:-6]
	result=re.search(pre2,text2)
#	text2=re.sub("^"+pre2,"",text2)
	i=result.start()
	text2=text2[i+5:-6]
	if re.match(text1,text2):
		return True
	else:
		return False


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
#	myfiles = os.listdir(pathname)
except Exception as e:
	print("path {} raises exception {}".format(pathname,e))
	os._exit(-1)

newfilename=""
myfiles.sort()
print("Length myfiles {}".format(len(myfiles)))
newfilename=os.path.join(pathname,"wheel_IDX_list.csv")
fnames=[]
idx=[]

x=0

with open(newfilename, mode='r') as f:
	line=f.readline()
	while line:
		fnames.append(line.split(",")[0])
		x=int((int(line.split(",")[1])-1)/2)
		if (x>=0 and x<8):
			idx.append(x)
		else:
			print("unexpected index")
			exit(0)
		line=f.readline()

listgood=(len(myfiles)==len(idx))
print(listgood)

if (listgood):  ##these must match.
	newfilename=os.path.join(pathname,"processLog.csv") 
	with open(newfilename,mode='w') as f:
		f.write("GSPEC file, W_IDX file,rawIndex,interpretedIndex,sampleID\n")
		for i in range(len(idx)):
			fnames[i]=re.sub("/home/pi/data/","",fnames[i]) ## list generated using os.listdir 
#			fnames[i]=re.sub(pathname,"",fnames[i]) ## list generated using os.listdir 
			myfiles[i]=re.sub(pathname,"",myfiles[i]) ## list generated using glob
			listgood=listgood and areSame("GSPEC",myfiles[i],"W_IDX",fnames[i])
			print("{}\t{}\t{}\t{}\t{}".format(myfiles[i],fnames[i],2*(idx[i])+1,idx[i],sample[idx[i]]))
			f.write("{},{},{},{},{}\n".format(myfiles[i],fnames[i],2*(idx[i])+1,idx[i],sample[idx[i]]))

print("list good={}".format(listgood))


if listgood:
	## open len(myfiles)
	for k in range(len(myfiles)):
		##open myfiles[i]
		in_filename=os.path.join(pathname,myfiles[k])
		with open(in_filename, mode='r') as f:
			myInfo=f.readline() #calibration coeff
			myInfo=f.readline() #remark,
			myInfo=f.readline() #remark, with version information
			if not re.search('VERSION', myInfo): # challenge that here
				print("Invalid histogram file")
				exit(0)
			line = f.readline() #livetime
			livetime[idx[k]]+=(int(line.split(",")[1])+1) #add 1 because this is zero based
			line = f.readline()
			while not(re.search('data',line) and line):
				line = f.readline()
			if len(line)==0:
				print("unexpected end of file and phrase data not found")
				exit(0)
			i=0
			line=f.readline()
			while (line and i<max_bins):
				try:
					mHistogram[idx[k]][i]+= int(line.split(",")[1])
					i+=1
				except ValueError:
					print("value error")
					exit(0)
				line=f.readline()
		sys.stdout.write(".")
		sys.stdout.flush()
	## write sums to file
	newfilename=os.path.join(pathname,"SortedAndSummedHistgrams.csv")
	with open(newfilename,mode='w') as f:
		f.write("{}\n".format(newfilename))
		f.write("Index")
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
				f.write(",{}".format(mHistogram[i][j]))
			f.write("\n")

print("\nDone")
os._exit(0)
