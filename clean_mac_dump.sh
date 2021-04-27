#!/bin/sh
#
if [ $# -lt 1 ]; then
   echo; echo "Must provide input file name as argument ... aborting"; echo
   exit
fi

infile=$1
if [ ! -f "${infile}" ]; then
   echo; echo "Cannot read input ${infile} ... aborting"; echo
   exit
fi

cat ${infile} | tr '\r' '\n' | sed -E 's/ *$//g'

exit
