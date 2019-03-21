#!/bin/sh

if [ $# -lt 1 ]; then
   exit
fi

infile=$1
if [ ! -r "${infile}" ]; then
   echo "File ${infile} not readable ... abort"
   exit
fi

extraheader=`grep -c 'press return' ${infile} | tr -cd '[:digit:]'`
if [ "${extraheader}" -gt 0 ]; then
   sed -e '1,/press return/ d' ${infile} | perl -e 'while (<>) { s/\s+$//; print "$_\n"; }' > ${infile}-fixed
else
   perl -e 'while (<>) { s/\s+$//; print "$_\n"; }' ${infile} > ${infile}-fixed
fi

if [ $# -gt 1 ]; then
   if expr "$2" : '[rR][eE][pP]' > /dev/null; then
      mv -f ${infile}-fixed ${infile}
   fi
fi

exit
