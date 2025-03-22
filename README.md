Mostly this is a backup of code written on the mac.

POSITRON EXPERIMENT DATA COLLECTION ROUTINE:

pi3:
Use crontab:
on minute 0 and minute 30 : Collect wheel position data. these are W_IDX files
on minute 29 and 59 : advance turret to the next positon

pi4
use crontab
on minute 0 and minute 30, grab filename (whose time stamp will be almost identical to W_IDX) and start MCA for 28 minutes. This saves GSPEC_files

All data organized by date of collection. e.g.
pi3: ~/data/<date>/(list of W_IDX files)
pi4: ~/data/<date>/(list of G_SPEC files)

copy all data to MAC/DATA/<date>
the python code saved here is used to analyze the data.

POSITRON EXPERIMENT DATA ANALYSIS ROUTINE:

the python files need to be in the directory ~/data/ with all sub-directories dates, and each sub-directory containing the raw W_IDX and GSPEC_ files

1. python3 listWheelPositions.py subdir
	this grabs the W_IDX files and compiles into filename and wheel position. The output file "wheel_IDX_list.csv" is used by processfiles.py

2. python3 processRegionalSums.py subdir
	opens GSPEC files and regionally sums spectra. Region definitions are at the top of the .py file. Summarizes and outputs to "regionalSums.csv"

3. python3 processfiles.py subdir
   
