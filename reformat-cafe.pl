#!/usr/bin/perl -w

# reformat conductivity calibration module dump file when
# logging mode has changed during the logging period from
# '3502 to 'CAFE'.
# usage:  % reformat-cafe.pl module_file_name_cafe > module_file_name_fixed
#
# writes time of change to stderr
#

use Time::Local;

@block = ();
$defltvishay = undef;
$lastsync = undef;
$startcal = undef;
$sampint = 120;
$nblock = 0;

while (<>) {

   if (/SAMPLING INTERVAL/) {
#SAMPLING INTERVAL IS    00:02:00
      $interval = substr($_,25,8);
      ($inthh, $intmm, $intss) = ($interval =~ /(\d+):(\d+):(\d+)/);
      $sampint = 60*((60*$inthh) + $intmm) + $intss;
   }


   if (/readOK/) {
      if ( scalar @block and ($lastsync =~ /LOG/) ) {
         $blocksize = scalar @block;

         for ( $i = 0, $n = 0; $i < $blocksize; $i += 2 ) {
            last if ( $block[$i] =~ /0000/ );
            print "$defltvishay $block[$i] $block[$i+1]";
            ++$n;
            if ( $n == 4 ) {
               print "\n";
               $n = 0;
            } else {
               print " ";
            }
         }
         print "\n";
         @block = ();
      }

      s/\s+$//;
      print "$_\n";
      last;
   }

   if (/^3502 \d{4}\/\d{2}\/\d{2}/) {
#3502 2008/12/10  17:56:02  00000 000D3 07AE2
      ++$nblock;
      ($blocktime, $blockvishay) = unpack "x5 a20 x3 a4", $_;
#      $vishay = hex($blockvishay);
      ($yyyy,$mn,$dy,$hh,$mm,$ss) = ($blocktime =~ /(\d+)\/(\d+)\/(\d+)  (\d+):(\d+):(\d+)/);
      $blockstart = timelocal($ss,$mm,$hh,$dy,$mn-1,$yyyy);

      s/\s+$//;
      print "$_\n";

      $startcal = (defined $startcal) ? 2 : 1;
      $lastsync='CAL';
      
      @block = ();
      while (<>) {
         if (/^\s*$/) {            # end of block: write out reformatted
            if ( scalar @block != 432 ) {
               printf STDERR "Unexpected block size (" . scalar @block . ") ... skipping this block\n";

               print "\n";

               @block = ();
               last;
            }

            $trunc = 0;
            if ( $block[$#block] =~ /0000/ ) {
               for ($i = $#block; $i > 0; --$i) {
                  if ( $block[$i] =~ /0000/ ) {
                     ++$trunc;
                  } else {
                     last;
                  }
               }
            }

            $complete = 144 - $trunc;
            if ($trunc) {
               $lastsync = 'LOG';
               $samptime = $blockstart + ($complete * $sampint);
               printf STDERR "\n !! Logging mode changed '3502' -> 'CAFE' in block %d on %s\n\n",
                             $nblock, scalar(localtime($samptime));
            }

            $n = 0;
            for ($i = 0, $j = 0; $j < $complete; $i += 3, ++$j) {
               $defltvishay = $block[$i];
               print "$block[$i] $block[$i+1] $block[$i+2]";
               ++$n;
               if ( $n % 4 ) {
                  print " ";
               } else {
                  print "\n";
                  $n = 0;
               }
            }

            for ($i = 3*$complete, $j = $complete; $j < 144; $i +=2, ++$j) {
               print "$defltvishay $block[$i] $block[$i+1]";
               ++$n;
               if ( $n % 4 ) {
                  print " ";
               } else {
                  print "\n";
                  $n = 0;
               }
            }

            last;
         }

#         chomp;
         s/\s+$//;
         push @block, split /\s+/, $_;
      }
      last unless defined($_);
   }

   if (/^CAFE \d{4}\/\d{2}\/\d{2}/) {
      s/CAFE/3502/;
      $blockvishay = unpack "x28 a4", $_;
       
      $blockvishay = $defltvishay if ($blockvishay =~ /0000/);
      $defltvishay = $blockvishay;

      s/\s+$//;
      print "$_\n";

      $lastsync='LOG';

      @block = ();
      while (<>) {
         if (/^\s*$/) {
            if ( ((scalar @block == 432) and $startcal) or
                 ((scalar @block == 288) and not defined $startcal) ) {
               for ( $i = 0, $j = 0, $n = 0; $j < 144; $i += 2, ++$j ) {
                  $defltvishay = $blockvishay = '0000' if ($block[$i] =~ /0000/);
                  print "$blockvishay $block[$i] $block[$i+1]";
                  ++$n;
                  if ( $n == 4 ) {
                     print "\n";
                     $n = 0;
                  } else {
                     print " ";
                  }
               }
            } else {
               printf STDERR "Unexpected block size (" . scalar @block . ") ... skipping this block\n";

               print "\n";

               @block = ();
               last;
            }

            s/\s+$//;
            print "$_\n";

            @block = ();
            last;
         }

#         chomp;
         s/\s+$//;
         push @block, split /\s+/, $_;
      }
      last unless defined($_);
      next;
   }

   s/\s+$//;
   print "$_\n";

}   

if ( scalar @block and ($lastsync =~ /LOG/) ) {
   $blocksize = scalar @block;

   for ( $i = 0, $n = 0; $i < $blocksize; $i += 2 ) {
      last if ( $block[$i] =~ /0000/ );
      print "$defltvishay $block[$i] $block[$i+1]";
      ++$n;
      if ( $n == 4 ) {
         print "\n";
         $n = 0;
      } else {
         print " ";
      }
   }
   print "\n";
}

exit 1;
