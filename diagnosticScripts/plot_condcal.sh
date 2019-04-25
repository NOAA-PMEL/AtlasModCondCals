#!/bin/sh
#
###
if [ $# -lt 1 ]; then
   echo "Must supply calibration ID, e.g. SB01175"
   exit
fi
#
calid=`echo $1 | cut -d"." -f1 | tr -cd "[:alnum:]" | tr "[A-Z]" "[a-z]"`
if [ $# -gt 1 ]; then
   gmtdiff=$2
else
   gmtdiff=8
fi
###
if [ $# -gt 2 ]; then
   calyear=$3
else
   calyear="20`expr "${calid}" : '[a-z]*\([0-9][0-9]\)[0-9]*'`"
fi
calday=`expr "${calid}" : '[a-z]*[0-9][0-9]\([0-9]*\)'`

TZ="Greenwich"; export TZ
caldir="/home/ketch/data/calibration/cond/${calyear}"
progdir="/home/ketch/taoproc/calcheck"
DUMP="${progdir}/dumpmod"
XRANGE="${progdir}/pt2range"
XGMT="${progdir}/calpt2gmt"
outdir="${progdir}/module"
newline='\n'
#
##
scriptfile="${calid}.gp"
##
calfile="${caldir}/${calid}.cal"
if [ ! -f "${calfile}" ]; then
   echo "${calfile} not found ... aborting"
   exit
fi

cd ${outdir}
rm -f *.out

nmods=0
for module in ${caldir}/*sb.${calday}
do
   nmods=`expr ${nmods} + 1`
#   echo "Processing ${module} ..."
   ${DUMP} ${module}
done

mm=1
for dump in *.out
do
   root=`echo ${dump} | cut -d"." -f1`
   sed -e '1 d' ${dump} | cut -d"," -f1,4,7 | sed -e 's/,/ /g' > ${root}.gpdat
   rm -f ${dump}
   eval label${mm}=${root}
   mm=`expr ${mm} + 1`
done
###
echo "# gnuplot script to plot module response for ${calid}" > ${scriptfile}
echo "#" >> ${scriptfile}
#
echo "set terminal png small color" >> ${scriptfile}
echo "#" >> ${scriptfile}
#
echo "set data style lines" >> ${scriptfile}
echo "set rmargin 12" >> ${scriptfile}
echo "set lmargin 10" >> ${scriptfile}
echo "#" >> ${scriptfile}
#
echo "set noclip" >> ${scriptfile}
echo "set xzeroaxis" >> ${scriptfile}
echo "set xdata time" >> ${scriptfile}
echo "set timefmt \"%d/%m/%y %H:%M:%S\"" >> ${scriptfile}
echo "set mxtics 5" >> ${scriptfile}
echo "set offsets 60,60,0,0" >> ${scriptfile}
echo "#" >> ${scriptfile}
#
###
# First plot all module dump files
###
echo "###" >> ${scriptfile}
echo "# First plot all module dump files" >> ${scriptfile}
echo "#" >> ${scriptfile}
#
echo "set output \"${calid}_0.png\"" >> ${scriptfile}
echo "set size 1.0,1.0" >> ${scriptfile}
echo "set origin 0,0" >> ${scriptfile}
echo "set title \"All Module Data\"" >> ${scriptfile}
echo "set xrange [:]" >> ${scriptfile}
echo "set logscale y" >> ${scriptfile}
echo "set yrange [:]" >> ${scriptfile}
echo "#" >> ${scriptfile}
#
echo "set multiplot" >> ${scriptfile}
echo "#" >> ${scriptfile}
#
echo "set size 1.0,0.4925" >> ${scriptfile}
echo "set origin 0,0.5075" >> ${scriptfile}
echo "set key outside samplen 3" >> ${scriptfile}
echo "set bmargin 0" >> ${scriptfile}
echo "set tmargin 3" >> ${scriptfile}
echo "set xtics mirror" >> ${scriptfile}
echo "set format x \"\"" >> ${scriptfile}
echo "set ylabel \"Temperature Delta Count\"" >> ${scriptfile}
echo "#" >> ${scriptfile}
#
echo "plot \\">> ${scriptfile}
#
nn=1
while [ "${nn}" -lt "${nmods}" ]
do
   eval module="\$label${nn}"
   echo "'${module}.gpdat' using 1:3 t \"${module}\", \\" >> ${scriptfile}
   nn=`expr ${nn} + 1`
done
eval module="\$label${nn}"
echo "'${module}.gpdat' using 1:3 t \"${module}\"" >> ${scriptfile}
echo "#" >> ${scriptfile}
#
#
echo "set origin 0,0.01" >> ${scriptfile}
echo "set bmargin 3" >> ${scriptfile}
echo "set tmargin 0" >> ${scriptfile}
echo "set xtics nomirror" >> ${scriptfile}
echo "set nokey" >> ${scriptfile}
echo "set title" >> ${scriptfile}
echo "set format x \"%02d-%b${newline}%H%M\"" >> ${scriptfile}
echo "set ylabel \"Conductivity Delta Count\"" >> ${scriptfile}
echo "#" >> ${scriptfile}
#
echo "plot \\" >> ${scriptfile}
nn=1
while [ "${nn}" -lt "${nmods}" ]
do
   eval module="\$label${nn}"
   echo "'${module}.gpdat' using 1:4 notitle, \\" >> ${scriptfile}
   nn=`expr ${nn} + 1`
done
eval module="\$label${nn}"
echo "'${module}.gpdat' using 1:4 notitle" >> ${scriptfile}
#
echo "set nomultiplot" >> ${scriptfile}
echo "#" >> ${scriptfile}
#
###
# Now plot 20-min interval at each calibration point
###
echo "###" >> ${scriptfile}
echo "# Now plot 20-min interval at each calibration point" >> ${scriptfile}
echo "#" >> ${scriptfile}
#
echo "#set yrange [-1:100]" >> ${scriptfile}
ncalpts=0
for calpt in `grep '  [0-9][0-9]:[0-9][0-9]:[0-9][0-9]' ${calfile} | tr -d '\r' | tr -s ' ' '+'`
do
   ncalpts=`expr ${ncalpts} + 1`
   calpt=`echo "${calpt}" | tr "+" " "`
   xrangestring=`${XRANGE} "${calpt}" "${gmtdiff}"`
   calptstring=`${XGMT} "${calpt}" "${gmtdiff}"`
   echo "#" >> ${scriptfile}
#
   echo "set output \"${calid}_${ncalpts}.png\"" >> ${scriptfile}
   echo "set size 1.0,1.0" >> ${scriptfile}
   echo "set origin 0,0" >> ${scriptfile}
   echo "set title \"Calibration Point ${ncalpts} : ${calpt}\"" >> ${scriptfile}
   echo "set xrange [${xrangestring}]" >> ${scriptfile}
   echo "#" >> ${scriptfile}
#
   echo "set multiplot" >> ${scriptfile}
   echo "#" >> ${scriptfile}
#
   echo "set size 1.0,0.4925" >> ${scriptfile}
   echo "set origin 0,0.5075" >> ${scriptfile}
   echo "set key outside samplen 3" >> ${scriptfile}
   echo "set bmargin 0" >> ${scriptfile}
   echo "set tmargin 3" >> ${scriptfile}
   echo "set xtics mirror" >> ${scriptfile}
   echo "set format x \"\"" >> ${scriptfile}
   echo "set ylabel \"Temperature Delta Count\"" >> ${scriptfile}
   echo "#" >> ${scriptfile}
#
   echo "plot \\">> ${scriptfile}
#
   nn=1
   while [ "${nn}" -le "${nmods}" ]
   do
      eval module="\$label${nn}"
      echo "'${module}.gpdat' using 1:3 t \"${module}\", \\" >> ${scriptfile}
      nn=`expr ${nn} + 1`
   done
   echo "'-' using 1:3 t \"Bath\" with impulses lt 0 lw 2" >> ${scriptfile}
   echo "${calptstring} 100" >> ${scriptfile}
   echo "e" >> ${scriptfile}
   echo "#" >> ${scriptfile}
#
#
   echo "set origin 0,0.01" >> ${scriptfile}
   echo "set bmargin 3" >> ${scriptfile}
   echo "set tmargin 0" >> ${scriptfile}
   echo "set xtics nomirror" >> ${scriptfile}
   echo "set nokey" >> ${scriptfile}
   echo "set title" >> ${scriptfile}
   echo "set format x \"%02d-%b${newline}%H%M\"" >> ${scriptfile}
   echo "set ylabel \"Conductivity Delta Count\"" >> ${scriptfile}
   echo "#" >> ${scriptfile}
#
   echo "plot \\" >> ${scriptfile}
   nn=1
   while [ "${nn}" -le "${nmods}" ]
   do
      eval module="\$label${nn}"
      echo "'${module}.gpdat' using 1:4 notitle, \\" >> ${scriptfile}
      nn=`expr ${nn} + 1`
   done
   echo "'-' using 1:3 notitle with impulses lt 0 lw 2" >> ${scriptfile}
   echo "${calptstring} 100" >> ${scriptfile}
   echo "e" >> ${scriptfile}
   echo "#" >> ${scriptfile}
#
   echo "set nomultiplot" >> ${scriptfile}
   echo "#" >> ${scriptfile}
done
#
echo "exit" >> ${scriptfile}
#
if [ ${ncalpts} -eq 0 ]; then
   echo "No calibration times found in ${calfile}  ...  Aborting"
   rm -f ${scriptfile} *.gpdat
   exit
fi
#
gnuplot ${scriptfile}
rm -f ${scriptfile} *.gpdat
#
exit
