#!/usr/bin/env python
"""
An automation script for Atlas Module CondCals.

This script parses the SeaBird bath file into the .cal and .autosal
files, creates the Julian date directory, and moves all files into the
created directory. Should be run inside the target year directory.

Example: ../2021 > A2CondCals 27Apr2021.AT1

Author: Daryn White; daryn.white@noaa.gov
Last Edit: 2022-05-09 DAW

"""
import os
import subprocess
import argparse
import re
import datetime


class DutyCycleError(Exception):
    def __init__(self, value=None):
        import sys

        sys.tracebacklimit = 0
        self.__msg = value

    def __str__(self):
        return str((self.__msg is not None and self.__msg) or "")


## Parse arguments
parser = argparse.ArgumentParser(
    prog="A2CondCals",
    description="Build files and get cell_info to begin a session of conductivity calibrations",
)
parser.add_argument("fl", metavar="file", help="Bath file from SeaBird")
args = parser.parse_args()

# Regex for cal, autosal, and cells
cal = r".+(?=\s{5,}(Drift|Bottle))"
sal = r"(?=\b(Drift|Bottle)\s).+"
cell = r"(?<=Serial Numbers:\s)([\s\d]{4}){5,}"
zero = r"Duty Cycle: 0\.0"

# Read the file & make the strings needed for new files
with open(args.fl, "r") as f:
    fl = f.read()
    calOut = re.search(cal, fl, re.DOTALL)
    salOut = re.search(sal, fl, re.DOTALL)
    cells = re.search(cell, fl, re.DOTALL)
    badBath = re.search(zero, fl, re.DOTALL)

# Get the date from the file name
dt = datetime.datetime.strptime(args.fl[:7], "%d%b%y")
jdt = dt.strftime("%y%j")  # julian date

# Check for "Duty Cycle: 0.0"
if badBath:
    raise DutyCycleError(
        f"Input File: {args.fl} has instances of 'Duty Cycle: 0.0'. DO NOT PROCESS!"
    )
if not salOut or not calOut:
    raise FileNotFoundError(f"Input file: {args.fl} does not have a proper Autosal run")

# Establish usable vars
baseName = "sb" + jdt
filePath = os.path.abspath(args.fl)

# Make the new directory and change to that working directory
if not os.path.exists(baseName):
    os.makedirs(baseName)
    print(f"The new directory is: {baseName}")
    os.chdir(baseName)
    with open(baseName + ".cal", "a") as calFile:
        calFile.write(calOut.group())
    with open(baseName + ".autosal", "a") as salFile:
        salFile.write(salOut.group())
    with open(baseName + ".load", "a") as loadFile:
        ## Nothing, just a placeholder
        loadFile.write("")
    os.rename(filePath, os.getcwd() + "/" + args.fl)
    out = subprocess.run("cell_info " + cells.group(), shell=True)
else:
    print("Directory already exists")
