#mcamain.py
import sys
import time
import re
import logging
import os
from datetime import datetime
import csv


max_bins            = 8192
histogram           = [0] * max_bins
myInfo="test"
nanotime=0
temperature=0.1
myfiles=[]
totaltime=0

## sums all histograms into one. not sorted 


def parse_device_info(info_string):
    components = info_string.split()
    settings = {}
    for i in range(0, len(components) - 1, 2):
        key = components[i]
        value = components[i + 1]
        if value.replace('.', '', 1).isdigit() and value.count('.') < 2:
            converted_value = float(value) if '.' in value else int(value)
        else:
            converted_value = value
        settings[key] = converted_value
    return settings


def writeHistogram2CSV(filename):
	global histogram
	global max_bins
	global myInfo
	global myfiles
	global totaltime
	with open(filename,mode='w') as f:
		f.write(myInfo)
		f.write(filename)
		f.write("Total counting time,{}\n".format(totaltime))
		for i in range(len(myfiles)):
			f.write(myfiles[i])
			f.write("\n")
		f.write("Channel,Count\n")
		for x in range(max_bins):
			f.write("{},{}\n".format(x,histogram[x]))



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

# get a list of filenames

for i in range(len(myfiles)):
	if re.match(pattern,myfiles[i]):
		newfilename=os.path.join(pathname,myfiles[i])
		print(newfilename)

		# open a file
		with open(newfilename, mode='r') as f:
			myInfo=f.readline()
			myInfo=f.readline()
			myInfo=f.readline()  #information is on the third line of the histo file
			if re.search('VERSION', myInfo):
				info_dict = parse_device_info(myInfo)
#		print("MAX Version:\t\t{}".format(info_dict.get('VERSION')))
				nanoTime = info_dict.get('t')
#		print("Discriminator:\t\t{}".format(info_dict.get('NOISE')))
#		print("Elapse Time:\t\t{}".format(nanoTime))
				temperature=info_dict.get('T1')
#		print("Temperature:\t\t{} C".format(info_dict.get('T1')))
			else:
				print("Invalid histogram file")
				exit(0)

			line = f.readline()
			while not(re.search('data',line) and line):
				line = f.readline()
			if len(line)==0:
				print("unexpected end of file and phrase data not found")
				exit(0)

			totaltime+=nanoTime
			i=0
			line=f.readline()
			while (line and i<max_bins):
				try:
					histogram[i]+= int(line.split(",")[1])
#			print("{},{}".format(i,histogram[i]))
					i+=1
				except ValueError:
					print("value error")
					exit(0)
				line=f.readline()

if len(myfiles)>1:
	newfilename=os.path.join(pathname,"SPEC_total.csv")
	writeHistogram2CSV(newfilename)
print("Done")
exit(0)
