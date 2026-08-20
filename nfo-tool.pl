#!/usr/bin/perl

# Perl Based .nfo updater for Emby/Plex/XMBC
#
# Very simple design, only tested on Emby
# Allows updating of year, actor, studio and tags
# Silly Duplicate Detection

use strict;
use warnings;
use Getopt::Long;

my $nfo_file;
my $actor_test;
my $year;
my $studio;
my $tag;
my $debug;

GetOptions(
    "nfo=s"    => \$nfo_file,
    "actor=s"  => \$actor_test,
    "year=i"   => \$year,
    "studio=s" => \$studio,
    "tag=s"    => \$tag,
    "debug=s"  => \$debug,
) or die("Error in command line arguments\n");

if (!$nfo_file) {
    die("No nfo_file given");
}

if (!$actor_test && !$year && !$studio && !$tag) {
    die("At least one checkfield is mandatory");
}

if ($debug) {
    print "NFO: " . $nfo_file . "\n";
}

my $nfo_file_w     = $nfo_file . ".tmp";
my $actor_exists   = 0;
my $tag_exists     = 0;
my $studio_exists  = 0;
my $studio_differs = 0;
my $year_exists    = 0;
my $year_differs   = 0;
my $line           = 0;

open(my $nfo_fh, '<', $nfo_file) or die "Error opening NFO File: $!";
open(my $wfh,    '>', $nfo_file_w) or die "Error opening Temp File: $!";

while (<$nfo_fh>) {
    my $parse = $_;
    if ($line == 0) {
        if ($parse =~ /xml/) {
            if ($debug) {
                print "XML Found\n";
            }
        }
        else {
            die "No XML File";
        }
    }
    if ($actor_test && $parse =~ /<name>$actor_test</) {
        $actor_exists = 1;
        if ($debug) {
            print $actor_test . " is here\n";
        }
    }
    if ($tag && $parse =~ /<tag>$tag</) {
        $tag_exists = 1;
        if ($debug) {
            print $tag . " is here\n";
        }
    }
    if ($studio && $parse =~ /<studio>/) {
        if ($parse =~ /<studio>$studio</) {
            $studio_exists = 1;
        }
        else {
            $studio_exists  = 0;
            $studio_differs = 1;
        }
        if ($debug) {
            print $studio . " is here\n";
        }
    }
    if ($year && $parse =~ /<year>/) {
        if ($parse =~ /<year>$year</) {
            $year_exists = 1;
        }
        else {
            $year_differs = 1;
            $parse =~ s/<year>.*?<\/year>/<year>$year<\/year>/;
            $year_exists = 1;
        }
        if ($debug) {
            if ($year_differs) {
                print $parse . " is here not " . $year . "\n";
            }
            else {
                print $year . " is here\n";
            }
        }
    }
    if ($parse =~ /<fileinfo>/) {
        if ($actor_test && !$actor_exists) {
            print $wfh "  <actor>\n    <name>$actor_test</name>\n  </actor>\n";
        }
        if ($tag && !$tag_exists) {
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

close($nfo_fh) or die "Error closing NFO File: $!";
close($wfh)    or die "Error closing Temp File: $!";
rename($nfo_file_w, $nfo_file) or die "Error replacing NFO File: $!";
