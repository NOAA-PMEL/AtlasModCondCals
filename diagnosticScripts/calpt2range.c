#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>

#include "atlas_time.h"

#define SEC_PER_HOUR   3600
#define PST8_CORR      (8*SEC_PER_HOUR)

#define INTERVAL_MINUS  1200
#define INTERVAL_PLUS   1200

int main ( int argc, char **argv )
{
   int    year;
   char   longmonth[12], rangemin[20], rangemax[20];
   struct tm   ts, *timstrct;
   atltime_t   sbtime1, sbtime2;

   if (argc < 2)
      exit(1);

   longmonth[0] = 0;
/*
** 11/20/99 20:41:31
**   or
** Saturday, November 20, 1999 20:41:31
*/
   if ( 6 == sscanf(*++argv, "%d%*c%d%*c%d %d%*c%d%*c%d",
                                 &ts.tm_mon, &ts.tm_mday, &year,
                                 &ts.tm_hour, &ts.tm_min, &ts.tm_sec)
          ||

        6 == sscanf(*argv, "%*s %s %d%*c %d %d%*c%d%*c%d",
                                 longmonth, &ts.tm_mday, &year,
                                 &ts.tm_hour, &ts.tm_min, &ts.tm_sec) )
   {
      if (longmonth[0])
      {
         ts.tm_mon = fullmon_index(longmonth);
         if (year > 1899)
            ts.tm_year = year - 1900;
         else
            ts.tm_year = year;
      }
      else
      {
         --ts.tm_mon;
         if (year < 75)
            ts.tm_year = year + 100;
         else
            ts.tm_year = year;
      }

      if (ts.tm_mon < 0)
         exit(0);
/*
      {
         fprintf( stderr, "** Error Reading Date/Time for Interval %d\n", interval_index );
         return 1;
      }
*/

/*
** Seabird is on Local Time (PST/PDT), Modules are GMT
*/
      sbtime1 = mktime_atlas(&ts);
      if ( --argc > 1 )
         sbtime1 += (SEC_PER_HOUR * atoi(*++argv));
      else
         sbtime1 += PST8_CORR;

      sbtime2 = sbtime1 + INTERVAL_PLUS;
      sbtime1 -= INTERVAL_MINUS;

      timstrct = gmtime_atlas (&sbtime1);
      strftime(rangemin, 18, "%d/%m/%y %H:%M:%S", timstrct);
      timstrct = gmtime_atlas (&sbtime2);
      strftime(rangemax, 18, "%d/%m/%y %H:%M:%S", timstrct);

      fprintf( stdout, "\"%s\":\"%s\"", rangemin, rangemax );

      exit(0);
   
   }
   
   exit(1);
}


/* ******************************  fullmon_index  ****************************** */
int fullmon_index ( char *monname )
{
   int    i, j;
   char   *month[] = {"January", "February", "March", "April",
                      "May", "June", "July", "August",
                      "September", "October","November","December"};
   
   j = strlen(monname);
   
   for ( i = 0; i < 12; i++ )
   {
      if ( 0 == strncmp( monname, month[i], j ) )
         return i;
   }
   return -1;
}

