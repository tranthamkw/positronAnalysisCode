import os
import sys
import re
import glob
import argparse
import numpy as np 
from scipy.optimize import curve_fit 
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

#sample=["D-Glucose II","L-Glucose II","Empty I","D-Glucose III","D-Glucose I","L-Glucose I","L-Glucose III","Empty II"]

"""
fits gaussian + logistic to peaks in provided ranges

"""

mybounds=[(1, 10, 10, 0, 1, 1), (np.inf, np.inf, np.inf, np.inf, np.inf, np.inf)]

def gaussian(x,a,x0,s,b,c,d):
	y= a*np.exp(-1.0*(x-x0)**2/(2*s**2))+ b + c/(1 + np.exp((x-x0)/d))
	return y

#															#
# ++++++++++++++++++++	START MAIN +++++++++++++++++++++++#
#															#

parser = argparse.ArgumentParser(
	prog='fitHistograms',
	description='Fits Gaussian+Logisic to all GSPEC files in passed directories seperated by commas. Only uses data in channels <start> to <stop>.',
	epilog="e.g. python fitHistogram.py <dir1,dir2,dir3...> <start ch> <end ch>")
parser.add_argument('directory',type=str,help='directory')
parser.add_argument('startch', type=int, help='start channel')
parser.add_argument('endch', type=int, help='end channel')

args = parser.parse_args()
pathlist=args.directory.split(",")
startch = args.startch
endch = args.endch

if (endch<startch):
	print("endch < startch. Dumbass.")
	exit(-1)

max_bins=8192
histogram=[0 for x in range(max_bins)]
ch=[0 for x in range(max_bins)]

xdata=[]
ydata=[]

filelist=[]
temperature=[]
timeidx=[]
a=[]
da=[]
x0=[]
dx0=[]
s=[]
ds=[]
b=[]
db=[]
c=[]
dc=[]
d=[]
dd=[]


for u in range(len(pathlist)):
	pathname=pathlist[u]
	# if a slash was passed, remove it.  add one at the end. this
	# essentially adds a slash if we forget to add it.
	re.sub("/","",pathname)
	pathname+="/"
	if not os.path.isdir(pathname):
		print(pathname+" is not an existing pathname")
		exit(-1)
	try:
		myfiles = glob.glob(pathname+"GSPEC*.csv")
	except Exception as e:
		print("path {} raises exception {}".format(pathname,e))
		os._exit(-1)

	myfiles.sort()
	print("Pathname: {}\tLength myfiles {}".format(pathname,len(myfiles)))

	for k in range(len(myfiles)):
		in_filename=myfiles[k]
		filelist.append(in_filename)
		with open(in_filename, mode='r') as f:
			myInfo=f.readline() #calibration coeff
			myInfo=f.readline() #remark,
			myInfo=f.readline() #remark, with version information
			if not re.search('VERSION', myInfo): # challenge that here
				print("Invalid histogram file")
				exit(0)
			result=re.search("T1",myInfo)
			i=result.start()
			substr1=myInfo[i+3:i+8]
			temperature.append(float(substr1))
			line = f.readline() #livetime
			livetime=(int(line.split(",")[1])+1) #add 1 because this is zero based
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
					histogram[i]=int(line.split(",")[1])
					ch[i]=i
					i+=1
				except ValueError:
					print("value error")
					exit(0)
				line=f.readline()

			result = re.search("_",in_filename) #pull time code from filename
			if result:
				i=result.start()
				substr1=in_filename[i+1:i+3]
				substr2=in_filename[i+3:i+5]
				substr3=in_filename[i-2:i]
				if u==0:
					myday=float(substr3)
					day=0
				else:
					day=float(substr3)-myday

				timeidx.append(day*24.0+float(substr1)+float(substr2)/60.0)

			xdata=ch[startch:endch]
			ydata=histogram[startch:endch]
#	guess for a, x0, s, b, c, d
			guess=[ydata[int(len(ydata)/2)]\
				,startch+(endch-startch)/2\
				,(endch-startch)/3\
				,ydata[0]+ydata[len(ydata)-1]\
				,ydata[len(ydata)-1]\
				,(endch-startch)/2]
			try:
				popt,copt = curve_fit(gaussian,xdata,ydata,guess,bounds=mybounds)
				a.append(popt[0])
				x0.append(popt[1])
				s.append(popt[2])
				b.append(popt[3])
				c.append(popt[4])
				d.append(popt[5])
				da.append(copt[0][0]**0.5)
				dx0.append(copt[1][1]**0.5)
				ds.append(copt[2][2]**0.5)
				db.append(copt[3][3]**0.5)
				dc.append(copt[4][4]**0.5)
				dd.append(copt[5][5]**0.5)
			except:
				print("error fitting on file "+in_filename)
				print("Guess {}".format(guess))
				a.append(0)
				x0.append(0)
				s.append(0)
				b.append(0)
				c.append(0)
				d.append(0)
				da.append(0)
				dx0.append(0)
				ds.append(0)
				db.append(0)
				dc.append(0)
				dd.append(0)


#now write all to new file
newfilename=os.path.join(pathname,"gaussianFits{}_{}.csv".format(startch,endch))
print("Output to: "+newfilename)

with open(newfilename,mode='w') as f:
	f.write("Fit to  y= a*EXP(-1.0*(x-x0)^2/(2*s^2))+ b + c/(1 + EXP((x-x0)/d))\n")
	f.write("inFile,hour,T,a,(a),x0,(x0),s,(s),b,(b),c,(c),d,(d)\n")
	for i in range(len(filelist)):
		f.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(filelist[i]\
			,timeidx[i]\
			,temperature[i]\
			,a[i],da[i]\
			,x0[i],dx0[i]\
			,s[i],ds[i]\
			,b[i],db[i]\
			,c[i],dc[i]\
			,d[i],dd[i]))

#
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

fig.set_size_inches(7, 5)

plt.errorbar(timeidx,x0,dx0,marker='o',ms=5,mec = 'Black', mfc = 'Blue',ls='',ecolor='Black',elinewidth=1)
plt.xlabel("Hour")
plt.ylabel("MCA Channel")
plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(12))
plt.gca().xaxis.set_minor_locator(ticker.MultipleLocator(2))
#plt.tick_params(axis='x', which='minor', bottom=False)
plt.title(r'Gaussian center fit $X_0$ {} to {}'.format(startch,endch))
plt.grid(color = 'DodgerBlue', linestyle = '--', linewidth = 0.5)
fig.savefig(os.path.join(pathname,'graphX0_{}_{}.png'.format(startch,endch)),dpi=300)

plt.clf()
plt.errorbar(timeidx,a,da,marker='o',ms=5,mec = 'Red', mfc = 'Orange',ls='',ecolor='Black',elinewidth=1)
plt.xlabel("Hour")
plt.ylabel("Counts/livetime")
plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(12))
plt.gca().xaxis.set_minor_locator(ticker.MultipleLocator(2))
#plt.tick_params(axis='x', which='minor', bottom=False)
plt.title(r'Gaussian amplitude a {} to {}'.format(startch,endch))
plt.grid(color = 'DodgerBlue', linestyle = '--', linewidth = 0.5)
fig.savefig(os.path.join(pathname,'graph_a_{}_{}.png'.format(startch,endch)),dpi=300)

plt.clf()
plt.errorbar(timeidx,s,ds,marker='o',ms=5,mec = 'Blue', mfc = 'DarkTurquoise',ls='',ecolor='Black',elinewidth=1)
plt.xlabel("Hour")
plt.ylabel(r'$\sigma$ (MCA Channels)')
plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(12))
plt.gca().xaxis.set_minor_locator(ticker.MultipleLocator(2))
#plt.tick_params(axis='x', which='minor', bottom=False)
plt.title(r'Gaussian stddev $\sigma$ {} to {}'.format(startch,endch))
plt.grid(color = 'DodgerBlue', linestyle = '--', linewidth = 0.5)
fig.savefig(os.path.join(pathname,'graph_s_{}_{}.png'.format(startch,endch)),dpi=300)


print("\nDone")



os._exit(0)
