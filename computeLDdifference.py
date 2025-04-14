import os
import sys
import re
import glob
from os.path import exists
import argparse
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np 
from scipy.optimize import curve_fit 

"""
fits gaussian + logistic to peaks in provided ranges

"""


def gaussian(x,a,x0,s,b,c,d):
        y= a*np.exp(-1.0*(x-x0)**2/(2*s**2))+ b + c/(1 + np.exp((x-x0)/d))
        return y


def fitmycurve(xin,yin,startch,endch):
	mybounds=[(1, 10, 10, 0, 1, 1), (np.inf, np.inf, np.inf, np.inf, np.inf, np.inf)]
	xdata=xin[startch:endch]
	ydata=yin[startch:endch]
#       guess for a, x0, s, b, c, d
	guess=[ydata[int(len(ydata)/2)]\
	,startch+(endch-startch)/2\
	,(endch-startch)/3\
	,ydata[0]+ydata[len(ydata)-1]\
	,ydata[len(ydata)-1]\
	,(endch-startch)/2]
	try:
		popt,copt = curve_fit(gaussian,xdata,ydata,guess,bounds=mybounds)
		a=popt[0]
		x0=popt[1]
		s=popt[2]
		b=popt[3]
		c=popt[4]
		d=popt[5]
		da=(copt[0][0]**0.5)
		dx0=(copt[1][1]**0.5)
		ds=(copt[2][2]**0.5)
		db=(copt[3][3]**0.5)
		dc=(copt[4][4]**0.5)
		dd=(copt[5][5]**0.5)
	except:
		print("error fitting")
		print("Guess {}".format(guess))
		a=(0)
		x0=(0)
		s=(0)
		b=(0)
		c=(0)
		d=(0)
		da=(0)
		dx0=(0)
		ds=(0)
		db=(0)
		dc=(0)
		dd=(0)

	return a,da,x0,dx0,s,ds,b,db,c,dc,d,dd

"""
Opens "masterSum.csv" in the directory of command line.

computes average <E>

computes average <D>

computes average <L>
"Usage:  python computeLDdiffernce <path-to-masterSum.csv> <Ch511keV> <Ch1275keV?
"""

sample=["D- II","L- II","Empty I","D- III","D- I","L- I","L- III","Empty II"]
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

Eavg=[0.0 for x in range(max_bins)]
Davg=[0.0 for x in range(max_bins)]
Lavg=[0.0 for x in range(max_bins)]

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

def smoothHistograms(pts,livetime):
	global EHistogram
	global LHistogram
	global DHistogram
	global Eavg
	global Davg
	global Lavg
	global max_bins

	time=float(livetime)/3600.0
	for ch in range(pts,max_bins-pts-2):
		temp=0.0
		for i in range(1,pts+1):
			temp+=(EHistogram[ch-i]+EHistogram[ch+i])
		temp+=EHistogram[ch]
		Eavg[ch]=temp/float(2*pts+1)
		Eavg[ch]=Eavg[ch]/time
	for ch in range(pts,max_bins-pts-2):
		temp=0.0
		for i in range(1,pts+1):
			temp+=(DHistogram[ch-i]+DHistogram[ch+i])
		temp+=DHistogram[ch]
		Davg[ch]=temp/float(2*pts+1)
		Davg[ch]=Davg[ch]/time
	for ch in range(pts,max_bins-pts-2):
		temp=0.0
		for i in range(1,pts+1):
			temp+=(LHistogram[ch-i]+LHistogram[ch+i])
		temp+=LHistogram[ch]
		Lavg[ch]=temp/float(2*pts+1)
		Lavg[ch]=Lavg[ch]/time



################### START MAIN



chlo = 350
chhi = max_bins
scale = False
allgood=True



parser = argparse.ArgumentParser(
        prog='computeLDdifference',
        description='Fits Gaussian',
        epilog="e.g. python computeLDdifference <path-to-master-sum> <EnergyCh511keV> <EnergyCh1275keV>")
parser.add_argument('pathname',type=str,help='path to master sum')
parser.add_argument('ch511', type=float, help='Channel for 511keV')
parser.add_argument('ch1275', type=float, help='Channel for 1275keV')

args = parser.parse_args()
pathname=args.pathname
ch511 = args.ch511
ch1275 = args.ch1275


argc=len(sys.argv)

pathname=re.sub("/","",pathname)

filename = pathname+"/masterSum.csv"
if not exists(filename):
	print("{}  not found".format(filename))
	os._exit(-1)

if (ch511>ch1275):
	print("Channel 511 > channel 1275")
	os._exit(-1)

cal_m = (1275.0-511.0)/(ch1275-ch511)
cal_b = 1275.0 - cal_m * ch1275
print(filename)


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
	same=True
	for k in range(1,len(livetime)):
		same=(livetime[k]==livetime[0])
	if not same:
		print("\nWARNING: LIVE-TIMES ARE NOT THE SAME")
		print(livetime)

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
#if scale:
#	calculateScaleFactor(chlo,chhi)
#else:
for i in range(max_idx):
	scaleFactor[i]=1.0

#print("Scale factors by sample location")
#for i in range(max_idx):
#	print("{}\t{}\t{}".format(i,sample[i],scaleFactor[i]))

scaleAndAverage()

# COMPUTE SMOOTHED AVERAGE

smoothHistograms(10,livetime[0])  #use the first live time to norm smoothed average


# fits
xin=[j for j in range(max_bins)]
fitsE1=fitmycurve(xin,Eavg,2400,3700)
fitsD1=fitmycurve(xin,Davg,2400,3700)
fitsL1=fitmycurve(xin,Lavg,2400,3700)

fitsE2=fitmycurve(xin,Eavg,6300,8000)
fitsD2=fitmycurve(xin,Davg,6300,8000)
fitsL2=fitmycurve(xin,Lavg,6300,8000)



# save master sum
energy=[0.0 for x in range(max_bins)]

final_filename=pathname+"/EDL_Histogram"+re.sub("/","",sys.argv[1])+".csv"
print("summed to {}".format(final_filename))
with open(final_filename,mode='w') as f:
	f.write(headerline)
	f.write("\n")
	f.write("LiveTime,{}\n".format(livetime[1]))
	f.write("Energy calibration: Ch511 Ch1275=,{},{}\n".format(ch511,ch1275))
	f.write("Scaling enabled,{}\n".format(scale))
	f.write("Scale factors by sample location NOT DONE\n")
#	for i in range(max_idx):
#		f.write("{},{},{}\n".format(i,sample[i],scaleFactor[i]))
	mytext=['a','da','x0','dx0','s','ds','b','db','c','dc','d','dd']
	f.write("parameter,fit511_E,fit511_D,fit511_L,,fit1275_E,fit1275_D,fit1275_L\n")

	for j in range(len(mytext)):
		f.write("{},{},{},{},,{},{},{}\n".format(mytext[j],\
		fitsE1[j],fitsD1[j],fitsL1[j],fitsE2[j],fitsD2[j],fitsL2[j]))

	f.write("ch,E,D,L,<E>,<D>,<L>,<D>-<E>,<L>-<E>,<D>-<L>\n")
	for j in range(max_bins):
		energy[j]=float(j)*cal_m+cal_b
		f.write("{},{},{},{},{},{},{},{},{},{}\n".format\
		(j,EHistogram[j],DHistogram[j],LHistogram[j],\
		Eavg[j],Davg[j],Lavg[j],\
		Davg[j]-Eavg[j],Lavg[j]-Eavg[j],Davg[j]-Lavg[j]))

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

mycolors=['DarkOrange','DarkOrchid','DarkSlateBlue','#00B050','Black']

fig.set_size_inches(7, 5)


plt.plot(energy,Eavg,c=mycolors[4],linewidth=1.1)
plt.plot(energy,Davg,c=mycolors[2],linewidth=1.1)
plt.plot(energy,Lavg,c=mycolors[0],linewidth=1,ls='--')
plt.legend(['<E>','<D>','<L>'],loc='upper right')
plt.xlabel("Energy (keV)")
plt.ylabel("Counts/channel/hour")
plt.suptitle("Totaled & Averaged spectra")
plt.title("Livetime={}s".format(livetime[1]))
plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(200))
plt.gca().xaxis.set_minor_locator(ticker.MultipleLocator(50))
plt.grid(color = 'DodgerBlue', linestyle = '--', linewidth = 0.5)
fig.savefig(os.path.join(pathname,"AllSpectra"+re.sub("/","",sys.argv[1])+".png"),dpi=300)
plt.clf()



temp=[0 for x in range(max_bins)]
for i in range(max_bins):
	temp[i]=Davg[i]-Eavg[i]
plt.plot(energy,temp,c=mycolors[2],linewidth=1)
temp=[0 for x in range(max_bins)]
for i in range(max_bins):
	temp[i]=Lavg[i]-Eavg[i]
plt.plot(energy,temp,c=mycolors[0],linewidth=1)
plt.xlabel("Energy (keV)")
plt.ylabel("Counts/channel/hour")
plt.suptitle("Empty Corrected D- and L- spectra")
plt.title("Livetime={}s".format(livetime[1]))
plt.legend(['<D>-<E>','<L>-<E>'], loc='upper right')
plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(200))
plt.gca().xaxis.set_minor_locator(ticker.MultipleLocator(50))
plt.grid(color = 'DodgerBlue', linestyle = '--', linewidth = 0.5)
fig.savefig(os.path.join(pathname,"ECorrectedSpectra"+re.sub("/","",sys.argv[1])+".png"),dpi=300)

plt.clf()

temp=[0 for x in range(max_bins)]
for i in range(max_bins):
	temp[i]=Davg[i]-Lavg[i]
plt.plot(energy,temp,c=mycolors[3],linewidth=1)
plt.xlabel("Energy (keV)")
plt.ylabel("Counts/channel/hour")
plt.suptitle("Enantiomer difference")
plt.title("Livetime={}s".format(livetime[1]))
plt.legend(['<D>-<L>'], loc='upper right')
plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(200))
plt.gca().xaxis.set_minor_locator(ticker.MultipleLocator(50))
plt.grid(color = 'DodgerBlue', linestyle = '--', linewidth = 0.5)
fig.savefig(os.path.join(pathname,"D-L_Spectra"+re.sub("/","",sys.argv[1])+".png"),dpi=300)

print("Done")
os._exit(0)
