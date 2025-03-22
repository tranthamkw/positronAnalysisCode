Mostly this is a backup of code written on the mac.

Positron data collection and analysis routine:

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

use python code here to analyze the data.

General analysis routine
