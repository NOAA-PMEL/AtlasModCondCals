To adjust the time by a constant amount for all data blocks in a module text data
dump file, use the script fix-module-time.pl

`> fix-module-time.pl module_file_name dd:hh:mm:ss > new_module_file_name`
or
`> fix-module-time.pl dd:hh:mm:ss module_file_name > new_module_file_name`

where
   module_file_name is the input file to adjust
   dd:hh:mm:ss is the amount to adjust each data block time
   new_module_file_name is the name of the new file with corrected times

if any of the dd, hh, mm, ss fields are negative, the time is subtracted from the
original module data time.

The script may be edited to always apply the same correction by changing the
assignment at about line 10 of the script that looks like

      @addtime = (0, 0, 1, 5);

If this is done, the 'dd:hh:mm:ss' argument is not needed when running the script.

Examples:

`> fix-module-time.pl 12345sb.245-clockerr 00:03:00:00 > 12345sb.245`

   adds 3 hours to every data block timestamp in input file 12345sb.245-clockerr,
   and writes to output file 12345sb.245


`> fix-module-time.pl 12345sb.245-clockerr -2:00:00:00 > 12345sb.245`

   subtracts 2 days from every data block timestamp in 12345sb.245-clockerr


`> fix-module-time.pl 12345sb.245-clockerr > 12345sb.245`

   uses the default correction value specified in script variable @addtime to
   adjust data block timestamps

