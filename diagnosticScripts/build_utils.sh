#!/bin/sh

ATLTIME_INCDIR="${HOME}/library/atlastime"
ATLTIME_OBJDIR="${HOME}/library/atlastime/objects"
ATLTIME_OBJs="${ATLTIME_OBJDIR}/atlas_time1.o ${ATLTIME_OBJDIR}/atlas_time2.o ${ATLTIME_OBJDIR}/xttotm.o"

cd ${HOME}/calcheck

echo "Compiling 'dumpmod' from presscal3.c"
gcc -o dumpmod presscal3.c

echo "Compiling 'pt2range' from calpt2range.c"
gcc -o pt2range calpt2range.c -I${ATLTIME_INCDIR} ${ATLTIME_OBJs}

echo "Compiling 'calpt2gmt' from calpt2gmt.c"
gcc -o calpt2gmt calpt2gmt.c -I${ATLTIME_INCDIR} ${ATLTIME_OBJs}

exit
