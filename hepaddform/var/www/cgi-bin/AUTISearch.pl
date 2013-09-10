#!/usr/bin/perl -w
#=========================================================================
#
#    AUTISearch.pl
#
#    Fetch a list of records by author/title search and return possible
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
use utf8;
use Unicode::Normalize qw( NFC );

use File::Basename;
# use lib '/usr/share/perl/5.10.1/CPAN';
use lib (&fileparse($0))[1].".";
use Encode;
use IO::Handle;
use LWP::UserAgent;
use Sys::Hostname;

use arwagner::crossref;
use arwagner::pubmed;
use arwagner::Ebsco;
use arwagner::WoS;
use arwagner::CGIHelper;
use arwagner::GVK;

use CGI;
### use CGI qw/ -oldstyle_urls/;
### $CGI::USE_PARAM_SEMICOLONS = 0; # Same as oldstyle_urls


#--------------------------------------------------

my $format =  "JSON";

# Mode full is slow, so for interactive use use "quick" which just asks
# crossref (slow enough)
my $mode   = "full";
$mode = "quick";

# Try to fetch data by author/title searches
my $au     = "";        # Authors
my $ti     = "";        # Article title
my $db     = "";        # database to search
my $wwwhost= "";

my $useragent          = "Mozilla/5.0 (X11; U; Linux amd64; rv:5.0) Gecko/20100101 Firefox/5.0 (Debian)";

#--------------------------------------------------
# WoS connection parameters
my $dbid       = "WOS";
my $depth      = "";          # empty == all times
my $editions   = "";					# empty == all subscribed
my $firstRec   = 1;
my $sort       = "Date";
my $numRecs    = 10;
# set times_cited to get this counter set at all
my $fields     = "times_cited get_parent";

#--------------------------------------------------
# Collect records fist then build up the overwriting
my %cxrec    = ();  # Results from CrossRef
my %inhrec   = ();  # Results from Inspec
my %pmrec    = ();  # Results from PubMed
my %arxivrec = ();  # Results from arXiv
my %wosrec   = ();  # Results from WoS
my %bookrec  = ();  # 
my %jrecord  = ();  # Results from Invenio (Journal data)

sub FetchPubmed($$) {
	my ($au, $ti) = @_;
	my $query = $au. "[Author] AND " . $ti . "[Title]";
	my $db = "Pubmed";
	# Get the IDs relevant, then fetch the data
	my @idlist = pubmed::ESearch($db, $query);
	return (@idlist);
}

#----------------------------------------------------------------------
sub ConstructPubMedOutput($@) {
	my ($mode, @idlist) = @_;
	my $db = "Pubmed";
	my $json = "";

	foreach my $id (@idlist) {
		my %pmrec = pubmed::EFetch($db, $id);
		
		my $label = "";

		# The label that should be shown to the user
		$label .= $pmrec{"abbrev"} . ", ";
		$label .= $pmrec{"vol"} . ", ";
		$label .= $pmrec{"page"};
		$label .= " (" . $pmrec{"year"} . ")";
		$label .= " / ";
		my $au = $pmrec{"AU"};
		my $aucount = (( $au =~ tr/;//) +1 );
		if ($aucount > 1) {
			$au =~ s/;.*//;
			$au .= " et.al. ";
		}
		$label .= $au;
		$label .= "'" . $pmrec{"title"} . "'";

		if (defined($pmrec{issn})) {
			%jrecord = CGIHelper::FetchISSN($pmrec{issn});
		}

		# Though most of the following hashes are empty use the cannoical
		# procedure to build up the final hash for export
		my %rec = CGIHelper::ConstructRecord(
			$mode,
			\%cxrec,  \%inhrec,  \%pmrec,  \%arxivrec, 
			\%wosrec, \%bookrec, \%jrecord
		);
		my $recjson = CGIHelper::MakeOutput("JSON", $mode, %rec);
		$recjson =~ s/^{//;
		$recjson =~ s/},$//;


		$json .= "{\n";
		$json .= '"label" : "' . $label . '"'; 
		$json .= "\n";
		$json .= $recjson;
		$json .= "},\n";
	}
	$json = '[' . $json . ']';
	return($json);
}

#----------------------------------------------------------------------
sub FetchWOS($$) {
	 my ($au, $ti) = @_;
	 my $wosdoi = ""; # DOIs from WoS are not realiable :S

	 if (($au ne "") and ($ti ne "")) {

		my $query = "au=($au) and ti=($ti)";
		my $res = WoS::SearchRetrieve($dbid, $query, $depth, $editions, 
     					 $sort, $firstRec, $numRecs, $fields);
		%wosrec = WoS::XML2Hash($res);

		# #---------- CrossRef
		# if (defined($wosrec{WOSDOI})) {
		# 	 my %cxrec = crossref::DOI2bib($wosrec{WOSDOI});
		# 	 $wosdoi = $cxrec{doi} if (defined($cxrec{doi}));
		# }
	}
	 #return($wosdoi);
}

#----------------------------------------------------------------------
sub ConstructWoSOutput($) {
	my ($mode) = @_;
	my $RecCount = $wosrec{RecCount};
	my $json = "";

	for (my $i = 0; $i < $wosrec{RecCount}; $i++) {
		my %jrecord = ();
		my $label = "";
		$label .= $wosrec{"$i-JI"} . ", ";
		$label .= $wosrec{"$i-VL"} . ", ";
		$label .= $wosrec{"$i-BP"} . "-" . $wosrec{"$i-EP"};
		$label .= " (" . $wosrec{"$i-PY"} . ")";
		$label .= " / ";
		my $au = $wosrec{"$i-AU"};
		my $aucount = (( $au =~ tr/;//) +1 );
		if ($aucount > 1) {
			$au =~ s/;.*//;
			$au .= " et.al. ";
		}
		$label .= $au;
		$label .= "'" . $wosrec{"$i-TI"} . "'";

		my %rec = ();
		for my $k (keys (%wosrec)) {
			next if (not ($k =~ m/^$i/));
			my $key = $k;
			$key =~ s/$i/0/g;
			$rec{$key} = $wosrec{$k};
		}

		# Set RecCount explicitly to 1 otherwise no data will be
		# generated.
		$rec{RecCount} = 1;

		# If we have an ISSN => resolve it. Use %rec as %wosrec has the
		# wrong counting
		if (defined($rec{"0-SN"})) {
			%jrecord = CGIHelper::FetchISSN($rec{"0-SN"});
		}

		# The following function copies all keys to the proper ones
		%rec = CGIHelper::ConstructRecord(
			$mode,
			\%cxrec,  \%inhrec,  \%pmrec,  \%arxivrec, 
			\%rec,    \%bookrec, \%jrecord
		);

		my $recjson = CGIHelper::MakeOutput("JSON", $mode, %rec);
		$recjson =~ s/^{//;
		$recjson =~ s/},$//;

		$json .= "{\n";
		$json .= '"label" : "' . $label . '", '; 
		$json .= "\n";
		$json .= $recjson;
		$json .= "},\n";
	}
	return($json);
}

#======================================================================

my $q = new CGI;

## print $q->header(-type=>'text/plain', -charset=>"utf-8");

$au     = $q->param("au");
$ti     = $q->param("ti");
$mode   = $q->param("mode");
$db     = $q->param("db");
$wwwhost= $q->param("wwwhost");

$wwwhost= hostname if (not(defined($wwwhost)));
$au   = ""     if (not(defined($au)));
$ti   = ""     if (not(defined($au)));
$mode = "thin" if (not(defined($au)));
$db   = "wos"  if (not(defined($au)));

CGIHelper::SetWWWHost($wwwhost);

my $dataoutput = "";
if (($au ne "") and ($ti ne "")) {
	if ($db eq "wos") {
		FetchWOS($au, $ti);
		$dataoutput = ConstructWoSOutput($mode);
	}
	elsif ($db eq "pubmed") {
		my @idlist = FetchPubmed($au, $ti);
		$dataoutput = ConstructPubMedOutput($mode, @idlist);
	}
	elsif ($db eq "gvk") {
		$dataoutput = GVK::AUTISearch($mode, $au, $ti);
	}
}

print encode('utf-8', NFC $dataoutput);

# open (OUT, ">out.xml");
# print OUT $dataoutput;
# close(OUT);

## foreach $c (@CK) {
## 	 print "   $c\n";
## }
