/*
** when using unix system with TZ environmental variable set,
** reset TZ to "Greenwich" to suppress daylight time assignment in call
** to localtime()
*/

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <ctype.h>
#include <time.h>
#include <limits.h>

#define FILE_SUFFIX				".out"
#define MAX_FNAME_LENGTH		80
#define MAX_REC_LENGTH			150
#define NEWLINE_CHAR			'\n'
#define SPACE_CHAR				0x20
#define STRING_END				0x00
#define COLON_CHAR				':'
#define EQUALS_CHAR				'='
#define BACKSLASH_CHAR			0x5C
#define SAMPLE_INTERVAL_ID		"SAMPLING INTERVAL IS"
#define SAMPLE_INTERVAL_ID2		"LOGGING INTERVAL IS"
#define SERIAL_NUMBER_ID		"SERIAL NUMBER IS"
#define DATA_START_ID			"3502 "

/* *************************  function prototypes  ************************** */
int		main ( int, char** );
int		read_header ( FILE*, int*, long* );
int		modfy_fname ( char*, char* );
int		time_to_str ( time_t, char * );



/* ***************************  global variables  *************************** */
FILE	*infile_fp, *outfile_fp;
char	infile_fname[MAX_FNAME_LENGTH],
		outfile_fname[MAX_FNAME_LENGTH];


/* ************************************************************************** */
/* ********************************  main  ********************************** */
int main ( int argc, char **argv )
{
	char	line_buffer[MAX_REC_LENGTH+1],
			scan_str[18];
	int			n, nn, i, jj, kk, sample_int, year;
	struct tm	tstruct;
	long		serialno;
	long		p[4],t[4], p_accum[10], t_accum[10];
	long		p_hi, p_lo, t_hi, t_lo, p_range, t_range;
	long		p_sdev, t_sdev;
	time_t		start_time;
/*
**  read command line argument if present, otherwise prompt for filename
*/
	infile_fname[0] = STRING_END;
	if ( argc-- > 1 )
	{
		infile_fp = fopen(*++argv, "r" );
		strcpy( infile_fname, *argv );
	}

	if ( infile_fp == NULL ) /* bad or missing input filename */
	{
		do
		{
			printf( "\nFile %s Cannot be Found\t** Try Again **\n", infile_fname );
			printf( "Enter Name for Input Data File or X to Exit : " );
			infile_fname[0] = STRING_END;
/* 			gets( infile_fname ); */
		    fgets( infile_fname, MAX_FNAME_LENGTH-1, stdin );
			if ( infile_fname[0] )
			{
				if ( infile_fname[0] == 'X' || infile_fname[0] == 'x' )
					return 1;
				infile_fp = fopen( infile_fname, "r" );
			}
		}
		while ( infile_fp == NULL );
	}

/*
**  Use input file name to create output file name
*/
	if ( read_header( infile_fp, &sample_int, &serialno ) )
	{
		fclose(infile_fp);
		return 1;
	}

/*
	modfy_fname( infile_fname, outfile_fname );
*/
	sprintf( outfile_fname, "%ld%s", serialno, FILE_SUFFIX);
	if ( (outfile_fp = fopen(outfile_fname, "w")) == NULL )
	{
	   fprintf(stderr, "Error opening output file %s\n", outfile_fname );
	   return 1;
	}

	fprintf( outfile_fp, "DT_%ld, TH_%ld, T_%ld, TR_%ld, CH_%ld, C_%ld, CR_%ld\n",
			serialno, serialno, serialno, serialno, serialno, serialno, serialno );

	jj = 0;
	p_range = t_range = 0;

	while ( fgets( line_buffer, MAX_REC_LENGTH, infile_fp) != NULL )
	{
/*
3502 1998/03/04  17:52:58  038A3 000D8 00229
*/
		if ( 6 != sscanf(line_buffer, "3502 %d/%d/%d  %d:%d:%d",
						&year, &tstruct.tm_mon, &tstruct.tm_mday,
						&tstruct.tm_hour, &tstruct.tm_min, &tstruct.tm_sec ) )
			break;
		--tstruct.tm_mon;
		tstruct.tm_year = year - 1900;
		tstruct.tm_isdst = 0;
		start_time = mktime(&tstruct);

		n = 0;
		do
		{
			if ( fgets( line_buffer, MAX_REC_LENGTH, infile_fp) == NULL )
				break;
			nn = sscanf( line_buffer,
					"%*lx %lx %lx %*lx %lx %lx %*lx %lx %lx %*lx %lx %lx",
					&t[0],&p[0],&t[1],&p[1],&t[2],&p[2],&t[3],&p[3] );

			nn /= 2;

			for ( i = 0; i < nn; i++,n++ )
			{
				time_to_str( start_time+(n*sample_int),scan_str );

				if ( jj < 10 )
				{
				     p_accum[jj] = p[i];
				     t_accum[jj] = t[i];
				     if ( ++jj > 9 )
				     {
	  				     p_hi = t_hi = LONG_MIN;
	  				     p_lo = t_lo = LONG_MAX;

	  				     for ( kk = 0; kk < 10; kk++ )
	  				     {
	  				         if (p_accum[kk] < p_lo)
	  				           p_lo = p_accum[kk];

	  				         if (p_accum[kk] > p_hi)
	  				           p_hi = p_accum[kk];

	  				         if (t_accum[kk] < t_lo)
	  				           t_lo = t_accum[kk];

	  				         if (t_accum[kk] > t_hi)
	  				           t_hi = t_accum[kk];
	  				     }
	  				     p_range = p_hi - p_lo;
	  				     t_range = t_hi - t_lo;
				     }
				}
				else
				{
				    for ( kk = 0; kk < 9; kk++)
				    {
				        p_accum[kk] = p_accum[kk+1];
				        t_accum[kk] = t_accum[kk+1];
				    }

				     p_accum[9] = p[i];
				     t_accum[9] = t[i];

				     p_hi = t_hi = LONG_MIN;
				     p_lo = t_lo = LONG_MAX;

				     for ( kk = 0; kk < 10; kk++ )
				     {
				         if (p_accum[kk] < p_lo)
				           p_lo = p_accum[kk];

				         if (p_accum[kk] > p_hi)
				           p_hi = p_accum[kk];

				         if (t_accum[kk] < t_lo)
				           t_lo = t_accum[kk];

				         if (t_accum[kk] > t_hi)
				           t_hi = t_accum[kk];
				     }
				     p_range = p_hi - p_lo;
				     t_range = t_hi - t_lo;
				}

				fprintf( outfile_fp, "%s,  %4lX,  %5d, %6d,  %4lX,  %5d, %6d\n",
									scan_str, t[i], t[i], t_range, p[i], p[i], p_range );

			}
		}
		while ( strlen(line_buffer) > 5);
/*
		fprintf( outfile_fp, "\n***\n\n" );
*/
	}

	if (infile_fp)
		fclose(infile_fp);
	if (outfile_fp)
		fclose(outfile_fp);

	return 0;
}

/* ****************************  read_header  ******************************* */
int read_header ( FILE *infile, int *interval_sec, long *serialno )
/*
** Read through file until out of header lines
*/

{
	int		hour, minute, second,
			end_header = 0,
			have_interval = 0,
			have_serial = 0;
	char	*bufptr,
			line_buffer[MAX_REC_LENGTH+1];
	long	flPos;

	flPos = ftell(infile);
	while ( fgets( line_buffer, MAX_REC_LENGTH, infile) != NULL )
	{

		if ( strstr( line_buffer, SAMPLE_INTERVAL_ID ) )
		{
			bufptr = line_buffer+strlen(SAMPLE_INTERVAL_ID);
			if ( sscanf( bufptr, " %d:%d:%d", &hour, &minute, &second ) != 3 )
				return 1;
			*interval_sec = hour*3600 + minute*60 + second;
			have_interval = 1;
		}

		if ( strstr( line_buffer, SAMPLE_INTERVAL_ID2 ) )
		{
			bufptr = line_buffer+strlen(SAMPLE_INTERVAL_ID2);
			if ( sscanf( bufptr, " %d:%d:%d", &hour, &minute, &second ) != 3 )
				return 1;
			*interval_sec = hour*3600 + minute*60 + second;
			have_interval = 1;
		}

		if ( strstr( line_buffer, SERIAL_NUMBER_ID ) )
		{
			bufptr = line_buffer+strlen(SERIAL_NUMBER_ID);
			if ( sscanf( bufptr, " %ld", serialno ) == 1 )
				have_serial = 1;
		}

		if ( strncmp(line_buffer, DATA_START_ID, 5) == 0 )
			break;

		flPos = ftell(infile);
	}

	if (!have_serial)
		*serialno = 99999;

	if (!have_interval)
	{
		fprintf( stderr, "** Unexpected End-of-File while Reading Header\n" );
		return 1;
	}

	fseek(infile, flPos, SEEK_SET);
/*
	fprintf( stderr, "Interval = %d Seconds\n", interval_sec );
	fprintf( stderr, "%s\n", line_buffer );
*/
	return 0;

}


/* ****************************  modfy_fname  ***************************** */
#define S_COLON 0x3B
#define DOT		0x2E

int modfy_fname ( char *in_fname, char *new_fname )
{
	int		n;
	char	*char_ptr;


/*
	n = 0;
	while ( in_fname[n] = toupper(in_fname[n]) )
		n++;
*/
	strcpy( new_fname, in_fname );
	if ( char_ptr == strrchr(new_fname, S_COLON) )
		*char_ptr = STRING_END;

	if ( char_ptr == strrchr(new_fname, DOT) )
		*char_ptr = STRING_END;
	strcat( new_fname, FILE_SUFFIX );

	return strlen(new_fname);
}
#undef S_COLON
#undef DOT

/* ****************************  time_to_str  ******************************* */
/*
** convert date/time string written in input file to time_t time for easy
** evaluation of gaps in adcp coverage.
*/
int	time_to_str ( time_t t_secs, char *td_str )
{
	char		*months[] = { "   ", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
							 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" };
	struct tm	*tstruct;

	tstruct = localtime( &t_secs );
	return sprintf( td_str, "%02d/%02d/%02d %02d:%02d:%02d",
						tstruct->tm_mday, tstruct->tm_mon+1,
						tstruct->tm_year%100, tstruct->tm_hour, tstruct->tm_min, tstruct->tm_sec );

}
