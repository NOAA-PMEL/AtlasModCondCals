#!/usr/bin/perl
use Date::Calc qw(Add_Delta_DHMS);

# add or subtract time correction to module dump file
# as written, file is re-written to standard output.
# usage:  % fix-module-time.pl module_file_name > new_module_file_name

# adjust array addtime to reflect desired correction:  @addtime = (dy, hh, mm, ss)
# if any of three are negative, correction is subtracted from time in file
################################################################################
@addtime = (0, 0, 1, 5);
################################################################################

@infiles = ();

foreach (@ARGV) {
   if (m/-?\d+:-?\d+:-?\d+/) {
      @addtime = split /:/;
      next;
   }
   if ( -f $_ ) {
      push(@infiles,$_);
   }
}
@ARGV = @infiles if @infiles;

if ($addtime[0] =~ m/^-/ ||
    $addtime[1] =~ m/^-/ ||
    $addtime[2] =~ m/^-/ ||
    $addtime[3] =~ m/^-/) {

  $addtime[0] = -abs($addtime[0]);
  $addtime[1] = -abs($addtime[1]);
  $addtime[2] = -abs($addtime[2]);
  $addtime[3] = -abs($addtime[3]);
}

while (<ARGV>) {
   if (/^3502|CAFE/) {
      if ( /\d{4}\/\d{2}\/\d{2}\s+\d{2}:\d{2}:\d{2}/) {
        chomp;
        my @fields = split;
        $newdate = fix_date($fields[1], $fields[2]);
        printf ("%s %s  %s %s %s\n", $fields[0], $newdate,@fields[3..5]);
        next;
      }
   }
   print;
}
exit 0;

sub fix_date {
  (my $datestring, my $timestring) = @_;
  ($year, $month, $day) = split '/', $datestring;
  ($hour, $minute, $second) = split ':', $timestring;
  
  ($yr2,$mo2,$dy2,$hr2,$mn2,$se) = Add_Delta_DHMS($year, $month, $day,$hour, $minute, $second,
                                                  $addtime[0], $addtime[1], $addtime[2], $addtime[3]);
  return sprintf( "%4d/%02d/%02d  %02d:%02d:%02d", $yr2,$mo2,$dy2,$hr2,$mn2,$se);
}
