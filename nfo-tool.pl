#!/usr/bin/perl

# Perl Based .nfo updater for Emby/Plex/XMBC
#
# Very simple design, only tested on Emby
# Allows updating of year, actor, studio and tags
# Silly Duplicate Detection

use Getopt::Long;

GetOptions ("nfo=s" => \$nfo_file,
            "actor=s"   => \$actor_test,
            "year=i"  => \$year,
	    "studio=s" => \$studio,
	    "tag=s" => \$tag,
	    "debug=s" => \$debug)
or die("Error in command line arguments\n");

	if (!$nfo_file) {
	   die ("No nfo_file given");
	}

	if (!$actor_test && !$year && !$studio && !$tag) {
	   die ("At least on checkfield is mandatory");
	}

	if ($debug) {
	   print "NFO: ".$nfo_file."\n";
	}

	$nfo_file_w = $nfo_file.".tmp";
  	open NFO_FILE,"<$nfo_file" or die "Error opening NFO File";
	open (my $wfh, '>', $nfo_file_w) or die "Error opening Temp File";
 	$line = 0;
	while (<NFO_FILE>) {
		$parse = $_;
		if ($line == 0) {
    		  if ($parse =~ /xml/) { 
 		    if ($debug) { 
                      print "XML Found\n";
		    }
		  } else {
  		    die "No XML File";
		  }
		}
		if ($actor_test && $parse =~ /<name>$actor_test</ ) {
		  $actor_exists = 1;
		  if ($debug) {
	            print $actor_test." is here\n";
		  }
		}
	 	if ($tag && $parse =~ /<tag>$tag</ ) {
		  $tag_exists = 1;
		  if ($debug) {
		    print $tag." is here\n";
		  }
		}
		if ($studio && $parse =~ /<studio>/ ) {
		    if ($parse =~ /<studio>$studio</ ) {
		      $studio_exists = 1;
                    } else {
                      $studio_exists = 0;
                      $studio_differs = 1;
                    }
		    if ($debug) {
                      print $studio." is here\n";
		    }
		}
		if ($year && $parse =~ /<year>/ ) {
 		  if ($parse =~ /<year>$year</ ) {
    		    $year_exists = 1;
		  } else {
 		    $year_exists = 1;
		    $year_differs = 1;
		  }
		  if ($debug) {
		    if ($year_differs) {
                      print $parse." is here not ".$year."\n";
		    } else {
		      print $year." is here\n";
		    }
		  }
		}
		if ($parse =~ /<fileinfo>/ ) {
		  if ($actor_test && $actor_exists < 1) {
 		    print $wfh "  <actor>\n    <name>$actor_test</name>\n  </actor>\n";
		  }
		  if ($tag && $tag_exists < 1) {
		    print $wfh "  <tag>$tag</tag>\n";
		  }
		}
		if ($parse =~ /<runtime>/ && $year && !$year_exists) {
		  print $wfh "  <year>$year</year>\n";
	        }
		if ($parse =~ /<fileinfo>/ && $studio && !$studio_exists) {
		  print $wfh "  <studio>$studio</studio>\n";
                }
	        print $wfh "$parse";
        	$line++;
	}
	close PW_FILE;
	close $whf;
 	rename $nfo_file_w, $nfo_file;
