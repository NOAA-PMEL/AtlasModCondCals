#!/usr/bin/env python3
## Building an automation script for Atlas Module CondCals
## Author: Daryn White; daryn.white@noaa.gov
# Last Edit: 2018-06-25 DAW 
import sys
import os
import argparse
import re
import datetime

## Parse arguments
parser = argparse.ArgumentParser(prog="A2CondCals",description="Build files and get cell_info to begin a session of conductivity calibrations")
parser.add_argument('fl',metavar='file',help='Bath file from SeaBird')
args = parser.parse_args()

# Find the cal part
cal = r".+(?=\s{14,}Drift)"
# Find the autosal part
sal = r"(?=\bDrift).+"

# Read the file & make the strings needed for new files
with open(args.fl,'r') as f:
  fl = f.read()
  calOut = re.search(cal,fl,re.DOTALL)
  salOut = re.search(sal,fl,re.DOTALL)

# print(calOut.group())
# print(salOut.group())
dt = datetime.datetime.strptime(args.fl[:7],'%d%b%y')
jt = dt.strftime('%y%j')
print(jt)