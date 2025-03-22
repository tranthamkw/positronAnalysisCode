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

## module which sums regions of individual spectra.  Called from external program.
## input histgram file must exist.
## appends summations to an outfile

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


def sumH(in_filename,chRegions):

	regionSum=[0 for x in range(len(chRegions)-1)]

	histogram           = [0] * max_bins
	with open(in_filename, mode='r') as f:
		myInfo=f.readline()
		myInfo=f.readline()
		myInfo=f.readline()
		if re.search('VERSION', myInfo):
			info_dict = parse_device_info(myInfo)
#			nanoTime = info_dict.get('t')
			temperature=info_dict.get('T1')
		else:
			print("Invalid histogram file")
			exit(0)
		line = f.readline()
		livetime = int(line.split(",")[1])+1 #live time is zero based
		while not(re.search('data',line) and line):
			line = f.readline()
		if len(line)==0:
			print("unexpected end of file and phrase data not found")
			exit(0)
		i=0
		line=f.readline()
		while (line and i<max_bins):
			try:
				histogram[i]= int(line.split(",")[1])
				i+=1
			except ValueError:
				print("value error. offending line:")
				print(line)
				exit(0)
			line=f.readline()

	for k in range(len(regionSum)):
		for i in range(chRegions[k],chRegions[k+1]-1):
			regionSum[k]+=histogram[i]


	tempstr="{},".format(in_filename)
	tempstr+="{},".format(temperature)
	tempstr+="{},".format(livetime)
	for k in range(len(regionSum)):
		tempstr+="{},".format(regionSum[k])
	tempstr+="{}\n".format(len(regionSum))

	return tempstr
