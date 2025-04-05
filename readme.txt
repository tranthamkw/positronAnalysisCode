
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

A. FOR EACH DAY (DIRECTORY)
	1. python3 listWheelPositions.py <subdir>
		this grabs the W_IDX files and compiles into filename and wheel position.
		The output file "wheel_IDX_list.csv" is used by processfiles.py

	2. python3 processRegionalSums.py <subdir>
		opens GSPEC files and regionally sums spectra. Region definitions are at the top of the .py file.
		Summarizes and outputs to "regionalSums.csv"

	3. python3 processfiles.py <subdir>
		*Opens wheel_IDX_list.csv and loads wheel index into an array
		*List all GSPEC files in the subdir
		*Compares that W_IDX and GSPEC time stamps match (date, hour, and minute)
		*Opens GSPEC files and adds to a histogram indexed by wheel location. we get a summed list of
		all spectra for each wheel location. ALSO sums livetime for each sample location.
		get an 8 (numsamples) by 8192 (numchannels) array of spectra.
		*output file 'SortedAndSummedHistograms.csv'

B. FOR EACH MULTIPLE DAY RUN-SET-EXPERIMENT

	4. python3 masterRegionalSums.py <dir1> <dir2> <dir3> . . .
		*<dir>'s should be given in time order
		*Opens 'RegionSums.csv' in each <dir>
		*The first dir starts the time index (based on filenames)
		*Appends each entry, to outfile 'masterRegionSum<lastdir>.csv'
		*Constructs graphs of temperature and region-sums as function of time

	5. python3 masterSumHistograms.py <dir1> <dir2> . . 
		*<dir>'s should be given in time order
		*Opens 'SortedAndSummedHistograms.csv' in each directory
		*Sums each of eight sample spectra. totals live time for each sample.
		*outputs to 'masterSum.csv' in the last <dir> passed.


	5. python3 computeLDdifference.py <dir>
		*<dir> is the directory with 'masterSum.csv'
		*Checks that livetime is the same for all eight samples
		*averages the two "Empty" sample spectra to one "E" spectra
		*averages the three "D-" sample spectra to one "D" spectra
		*averages the three "L-" sample spectra to one "L" spectra
		*Performs a smoothing and normalization operation: 
			for each channel of each spectra, compute average based on +/- 10 channels 
			Divides by livetime in hours
			Three final spectra <E>, <D>, <L>
		*outputs <E>, <D>, <L>, <E>-<D>, <E>-<L>, <D>-<L>
		* and graphs of these
