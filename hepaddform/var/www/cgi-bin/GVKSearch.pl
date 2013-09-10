#!/usr/bin/perl -w
#=========================================================================
#
#    ISBNSearch.pl
#
#    Fetch a list of records by ISBN search in GVK and return possible
#    matches as JSON
#
#    $Id: $
#    Last change: <Mi, 2012/06/20 11:29:21 cdsware zb0027.zb.kfa-juelich.de>
#    Author     : Alexander Wagner
#    Language   : Perl
#
#-------------------------------------------------------------------------
#
#    Copyright (C) 2011 by Alexander Wagner
#
#    This is free software; you can redistribute it and/or modify it
#    under the terms of the GNU Genereal Public License as published
#    by the Free Software Foundation; either version 2, or (at your
#    option) any later version.
#
#    This program is distributed in the hope that it will be usefull,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#    General Public License for more details.
#
#    You should have recieved a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
#=========================================================================

use strict;
use locale;
use utf8;
use Unicode::Normalize qw( NFC );
use File::Basename;
# use lib '/usr/share/perl/5.10.1/CPAN';
use lib (&fileparse($0))[1].".";
use Encode;
use IO::Handle;
use LWP::UserAgent;
use Sys::Hostname;

use arwagner::GVK;

use CGI;
### use CGI qw/ -oldstyle_urls/;
### $CGI::USE_PARAM_SEMICOLONS = 0; # Same as oldstyle_urls


#--------------------------------------------------

# Try to fetch data by author/title searches
my $isbn   = "";        # ISBN
my $au     = "";        # author
my $ti     = "";        # title
my $mode   = "";
my $format = "";
my $wwwhost= "";

my $useragent          = "Mozilla/5.0 (X11; U; Linux amd64; rv:5.0) Gecko/20100101 Firefox/5.0 (Debian)";

#--------------------------------------------------
# Collect records fist then build up the overwriting
my %bookrec = ();  # Results from CrossRef

#======================================================================


my $q = new CGI;

## print $q->header(-type=>'text/plain', -charset=>"utf-8");

$isbn   = $q->param("isbn");
$au     = $q->param("au");
$ti     = $q->param("ti");
$mode   = $q->param("mode");
$format = $q->param("format");
$wwwhost= $q->param("wwwhost");

CGIHelper::SetWWWHost($wwwhost);

$wwwhost= hostname if (not(defined($wwwhost)));
$isbn   = "" if (not(defined($isbn)));
$au     = "" if (not(defined($au)));
$ti     = "" if (not(defined($ti)));
$mode   = "fast" if (not(defined($mode)));
$format = "JSON" if (not(defined($format)));


my $dataoutput = "";
if ($isbn ne "") {
	print encode('utf-8', NFC GVK::FetchISBN($mode, $isbn));
}
if (($au ne "") and ($ti ne "")) {
	print encode('utf-8', NFC GVK::AUTISearch($mode, $au, $ti));
}

print $dataoutput;

