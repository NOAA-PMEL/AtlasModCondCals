#!/usr/bin/env python3
## Building an automation script for Atlas Module CondCals
## Author: Daryn White; daryn.white@noaa.gov
# Last Edit: 2018-06-25 DAW 
import sys
import os
import argparse
import re

## Parse arguments
parser = argparse.ArgumentParser(prog="A2CondCals",description="Build files and get cell_info to begin a session of conductivity calibrations")
parser.add_argument('fl',metavar='file',help='AT1/bath file from SeaBird')
args = parser.parse_args()

# Find the cal part
cal = re.compile(r".+(?=\s{14,}Drift)")
# Find the autosal part
sal = re.compile(r"(?=\bDrift).+")

# Read the file
with open(args.fl,'r') as f:
  data = f.read()
  # print(data)
  calOut = cal.match(data)
  print(calOut)