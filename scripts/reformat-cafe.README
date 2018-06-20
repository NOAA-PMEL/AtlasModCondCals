There is a new procedure for handling data from modules that change from
calibration mode to normal logging mode during the calibration process (any time
between set up here in the lab until returned to the lab for calibration data
processing).  The most critical data continues to be logged by the module, and
can be reformatted to be read by the calibration program.  This process saves
the cost of recalibration in the cases where the module data otherwise pass
the calibration criteria.  Reformatting is done with a script (reformat-cafe.pl)
that is on the server where the calibration processing is done.

When downloading module data, if you note that the logging mode changes from
'3502' to 'CAFE', continue downloading data as usual.  Name/rename the
downloaded data file something like '12345sb.123-cafe' (as opposed to the normal
convention '12345sb.123').  Transfer the file with the others to the calibration
directory on the server ketch.

Log into the server ketch and move to the calibration directory where the
module data files were transferred, e.g.

   cd /home/ketch/data/calibration/cond/2009

Run the reformatting script in the calibration script directory, using the
file name as an argument, and directing the output to a new file named in the
normal convention for the module data files.  For example:

% /home/ketch/data/calibration/scripts/reformat-cafe.pl 12345sb.123-cafe > 12345sb.123

will read from the file 12345sb.123-cafe and create a new file named 12345sb.123
that is formatted to work with the calibration program.

The script will also write out to the terminal the date and time at which the
logging mode change occurred.  (These diagnostic messages may help to identify
some event or procedure that is causing the change.)

After reformatting, the module data files should be readable by the calibration
program just as the normal files.
