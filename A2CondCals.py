#!/usr/bin/env python3
## Building an automation script for Atlas Module CondCals
## Author: Daryn White; daryn.white@noaa.gov
## Last Edit: 2018-07-24 DAW 
import sys
import os
import subprocess
import argparse
import re
import datetime

## Parse arguments
parser = argparse.ArgumentParser(prog="A2CondCals",description="Build files and get cell_info to begin a session of conductivity calibrations")
parser.add_argument('fl',metavar='file',help='Bath file from SeaBird')
args = parser.parse_args()

# Regex for cal, autosal, and cells
cal = r".+(?=\s{14,}Drift)"
sal = r"(?=\bDrift).+"
cell = r"(?<=Serial Numbers:\s)([\s\d]{4}){10,}"

# Read the file & make the strings needed for new files
with open(args.fl,'r') as f:
  fl = f.read()
  calOut = re.search(cal,fl,re.DOTALL)
  salOut = re.search(sal,fl,re.DOTALL)
  cells = re.search(cell,fl,re.DOTALL)

# Get the date from the file name
dt = datetime.datetime.strptime(args.fl[:7],'%d%b%y')
jdt = dt.strftime('%y%j') # julian date
# Establish usable vars
baseName = 'sb' + jdt
filePath = os.path.abspath(args.fl)
# Make the new directory and change to that working directory
if not os.path.exists(baseName):
  os.makedirs(baseName)
  os.chdir(baseName)
  with open(baseName+'.autosal', 'a') as salFile:
    salFile.write(salOut.group())
  with open(baseName+'.cal', 'a') as calFile:
    calFile.write(calOut.group())
  with open(baseName+'.load','a') as loadFile:
    ## Nothing, just a placeholder
    loadFile.write('')
  os.rename(filePath, os.getcwd()+'/'+args.fl)
  out = subprocess.run('cell_info ' + cells.group(), shell=True)
else:
  print("Directory already exists")
