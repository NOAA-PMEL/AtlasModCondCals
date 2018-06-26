#!/usr/bin/env python2
## Building an automation script for Atlas Module CondCals
## Author: Daryn White; daryn.white@noaa.gov
# Last Edit: 2018-06-25 DAW 
import sys
import argparse
import re

## Parse arguments
parser = argpase.ArgumentParser(prog="A2CondCals",description="Build files and get cell_info to begin a session of conductivity calibrations")
parser.add_argument('fl',metavar='file',help='AT1/bath file from SeaBird')

