#!/bin/sh

if [ $# -lt 1 ]; then
   echo "Must provide a space-separated list of cell numbers ... Aborting"
   exit
fi

cell_list=$@

MYSQL="mysql -N -h yawl TAO_cal"

echo;
for cell in ${cell_list}
do
   sql="SELECT TempInfo.module_type,TempInfo.sensor_id,ModCell.cell_id \
FROM TempInfo,ModCell \
WHERE TempInfo.sensor_id=ModCell.module_id \
AND cell_type='C' \
AND cell_id=${cell} \
ORDER BY ModCell.built_dt DESC \
LIMIT 1;"
#    echo ${sql}
   result=`${MYSQL} --execute="${sql}" | tr -cd '[:alnum:]\t\n'`
   if [ -n "${result}" ]; then
      echo ${result}
   else
      echo "*** No result for cell ${cell}"
   fi
done

echo
exit
