package Ebsco;
#=========================================================================
#
#    Ebsco.pm
#
#    EIT Web Service WSDL
#    http://eit.ebscohost.com/Services/SearchService.asmx?WSDL  
#    EIT: Web Service SearchService Page
#    http://eit.ebscohost.com/Pages/ServiceDescription.aspx?service=~/Services/SearchService.asmx    
#    Updated EIT: Web Service Documentation
#    http://support.ebsco.com/eit/ws.php
#    More useful documentation:
#    http://support.epnet.com/knowledge_base/detail.php?id=4242   
#
#    Example REST call:
#    http://eit.ebscohost.com/Services/SearchService.asmx/Search
#           ?prof=s6226163.main.eitws
#           &pwd=ebs5590
#           &authType=profile
#           &ipprof=
#           &query=education+and+teacher+not+student+and+dt+2006
#           &startrec=1
#           &numrec=10
#           &db=aph
#           &sort=date
#           &format=full
#
#    Database names: http://support.epnet.com/knowledge_base/detail.php?id=3783
#    http://eit.ebscohost.com/Services/SearchService.asmx/Info?prof=s6226163.main.eitws&pwd=ebs5590&authType=&ipprof=
#    aph       Academic Search Premier
#    inh       Inspec
#    psyh      PsycINFO
#    lxh       Library, Information Science & Technology Abstracts
#
#    Module to access the Ebsco Host databases  from Perl
#
#    $Id: $
#    Last change: <Mi, 2012/01/18 15:35:35 cdsware zb0027.zb.kfa-juelich.de>
#    Author     : Alexander Wagner
#    Language   : Perl
#
#-------------------------------------------------------------------------
#
#    Copyright (C) 2008 by Alexander Wagner
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

use Exporter;
use vars qw($VERSION @ISA @EXPORT);
$VERSION = "0.01";

use LWP::UserAgent;
use XML::XPath;
use Encode;
use IO::Handle;
use HGF::Forms::HGF;

*STDOUT->autoflush(1);    # Unbuffered screen IO

@ISA    = ('Exporter');
@EXPORT = qw();

#======================================================================

my $WSURL    = "http://eit.ebscohost.com/Services/SearchService.asmx";
my $SEARCH   = "Search";
my $PROF     = "s6226163.main.eitws";
my $PWD      = "ebs5590";
my $AUTHTYPE = "profile";
my $IPPROF   = "";
my $DB       = "";

my $query    = "";
my $startrec = 1;
my $numrec   = 10;
my $sort     = "date";
my $format   = "full";
my $useragent= "Perl";

#----------------------------------------------------------------------
=head2 XML2Hash

Extracts fields from an XML structure ot a hash tagged with the usual
2 char WoS tags. In case of Ebsco Host many fields are empty, as the WS
does not deliver enough information

Fields to export are:
	FN ISI Export Format
	VR 1.0
	PT, AU, AF, TI, SO, LA, DT, ID, AB, C1, RP, EM, NR, TC, PU, PI, PA,
	    *   *   *   *   *   *   *   *   *   *   *   *   *   x   x   x
	SN, J9, JI, PD, PY, VL, IS, BP, EP, DI, PG, SC, GA
	x   *   x   *   *   *   *   *   *   *   *   x   x
	UT ISI:<ut>

Fields marked with x are not contained in the dataset retrieved by WSDL.

Status: checked

=cut
#----------------------------------------------------------------------
sub XML2Hash($) {

	my ($rec) = @_;

	# Check, if at least one record was retrieved, otherwise xpath is
	# not happy...
	if ($rec =~ /\<rec /) {
		my $xmlxpath = XML::XPath->new(xml=>$rec);

		my $REC = $xmlxpath->find("//rec");
		my $rno = 0;
		foreach $entry ($REC->get_nodelist) {
			$data{"$rno-SRC"} = "Inspec";
			$data{"$rno-DT"}  = "" . $entry->find('header/controlInfo/artinfo/doctype');

			$data{"$rno-UT"}  = "" . $entry->find('header/@shortDbName') . ":" . $entry->find('header/@uiTerm');
			$data{"$rno-TI"}  = "" . $entry->find('header/controlInfo/artinfo/tig/atl');
			$data{"$rno-SO"}  = "" . $entry->find('header/controlInfo/jinfo/jtl');
			# $data{"$rno-J9"}  = ""; # $entry->find('item/source_abbrev');

			$data{"$rno-LA"}  = "" . $entry->find('header/controlInfo/language');
			$data{"$rno-AB"}  = "" . $entry->find('header/controlInfo/artinfo/ab');
			# $data{"$rno-RP"}  = ""; # $entry->find('item/reprint/rp_author');
			# $data{"$rno-RP"} .= ""; # ", " . $entry->find('item/reprint/rp_address') . ".";
			$data{"$rno-PY"}  = "" . $entry->find('header/controlInfo/pubinfo/dt/@year');
			$data{"$rno-VL"}  = "" . $entry->find('header/controlInfo/pubinfo/vid');
			$data{"$rno-BP"}  = "" . $entry->find('header/controlInfo/artinfo/ppf');
			$data{"$rno-EP"}  = "" . $entry->find('header/controlInfo/artinfo/ppct');
			$data{"$rno-PG"}  = "" . $entry->find('header/controlInfo/chapinfo/pages');
			# $data{"$rno-NR"}  = ""; # 
			# $data{"$rno-TC"}  = ""; # $entry->find('./@timescited');

			# $data{"$rno-CK"}  = ""; # $entry->find('item/i_ckey');
			
			$data{"$rno-DI"}  = "" . $entry->find('header/controlInfo/artinfo/ui[@type="doi"]');
			$data{"$rno-IS"}  = "" . $entry->find('header/controlInfo/pubinfo/iid');
			$data{"$rno-PU"}  = "" . $entry->find('header/controlInfo/pubinfo/pub');
			# $data{"$rno-PA"}  = ""; # $entry->find('issue/copyright/pub_address');
			# $data{"$rno-PI"}  = ""; # $entry->find('issue/copyright/pub_city');
			$data{"$rno-SN"}  = "" . $entry->find('header/controlInfo/jinfo/issn');
			# The issn should contain a - by convention
			$data{"$rno-SN"}  = substr($data{"$rno-SN"}, 0,4) . "-" .
													substr($data{"$rno-SN"}, 4,4);
			# $data{"$rno-JI"}  = ""; # $entry->find('issue/abbrev_iso');
			# $data{"$rno-PD"}  = "";
			# $data{"$rno-PT"}  = ""; # $entry->find('issue/pubtype/@code');
			# $data{"$rno-GA"}  = ""; # $entry->find('issue/ids');
			$data{"$rno-ISBN"}  = "" . $entry->find('header/controlInfo/bkinfo/isbn');
			$data{"$rno-pub"}   = "" . $entry->find('header/controlInfo/pubinfo/pub');
			$data{"$rno-place"} = "" . $entry->find('header/controlInfo/pubinfo/place[1]');
			if (defined($entry->find('header/controlInfo/pubinfo/place[2]'))) {
				$data{"$rno-place"} = $data{"$rno-place"} . ' [u. a.]';
			}
			$data{"$rno-btl"}   = "" . $entry->find('header/controlInfo/bkinfo/btl');

			$au = "";
			$af = "";
			for (my $i=1; $i <= $entry->find('count(header/controlInfo/bkinfo/aug/au)'); $i++) {
				$au .= $entry->find("header/controlInfo/bkinfo/aug/au[$i]") . "\t";
			}
			$au =~ s/\n//g;
			$af =~ s/\n//g;
			$data{"$rno-AU"} = $au;
			$data{"$rno-AF"} = $af;

			$sc = "";
			for (my $i=1; $i <= $entry->find('count(header/controlInfo/artinfo/classification)'); $i++) {
				$sc .= $entry->find("header/controlInfo/artinfo/classification[$i]") . "\t";
			}
			$data{"$rno-SC"} = $sc;

			$kw = "";
			for (my $i=1; $i <= $entry->find('count(header/controlInfo/artinfo/su)'); $i++) {
				$kw .= $entry->find("header/controlInfo/artinfo/su[$i]") . "\t";
			}
			$data{"$rno-ID"} = $kw;
			$data{"$rno-DE"} = $kw;

			$c1 = "";
			$data{"$rno-C1"} = $c1;

			$em = "";
			$data{"$rno-EM"}  = $em;

			$an = "";
			$rno++;
		}
		$data{"RecCount"} = $rno;
	}
	else {
		$data{"RecCount"} = 0;
	}

	return(%data);
}

#----------------------------------------------------------------------
=head2 ToEndNote

Stores result XML structure in EndNote import format as used by ISI.
Note: for the searchRetrieve the value of fields has to contain the
options "times_cited" and "get_parent" for all fields to be filled in!

Fields to export are:

	FN ISI Export Format
	VR 1.0
	PT, AU, AF, TI, SO, LA, DT, ID, AB, C1, RP, EM, NR, TC, PU, PI, PA,
	SN, J9, JI, PD, PY, VL, IS, BP, EP, DI, PG, SC, GA, UT 

Status: checked

=cut
#----------------------------------------------------------------------
sub ToEndNote($$) {
	my ($rec, $enlfile) = @_;
	my %data = ();

	# Define the fields to export as well as their chonological order
	my @fields = ( "PT", "AU", "AF", "TI", "SO", "LA", "DT", "ID",
		"AB", "C1", "RP", "EM", "NR", "TC", "PU", "PI", "PA", "SN",
		"J9", "JI", "PD", "PY", "VL", "IS", "BP", "EP", "DI", "PG",
		"SC", "GA", "UT");

	open (ENL, ">>$enlfile") or die "Can't open $enlfile: $!\n";

	%data = XML2Hash($rec);

	print ENL "FN ISI Export Format\n";
	print ENL "VR 1.0\n";
	for ($i=0; $i < $data{"RecCount"}; $i++) {
		foreach $key (@fields) {
			if (defined($data{"$i-$key"})) {
				$value = $data{"$i-$key"};
				if (($key =~ m/AU/) or 
					 ($key =~ m/AF/) or
					 ($key =~ m/EM/) or
					 ($key =~ m/CR/) or
					 ($key =~ m/C1/) or
					 ($key =~ m/ID/) or
					 ($key =~ m/SC/)) {
					$value =~ s/\t\s*$//;
					$value =~ s/\t /\n   /g;
				}
				print ENL "$key $value\n";
			}
		}
		print ENL "\n";
	}
	close(ENL);
}

#----------------------------------------------------------------------
=head2 ToTabWin

Stores XML structure in ISIs usual "Tab Delimited Windows" format.

Fields to export are:

	EM	CR	NR	TC	PU	PI	PA	SN	BN	DI	J9	JI	PD	PY	VL	IS	PN	SU	SI	BP	EP	AR
	DI	PG	SC	GA	UT

	UT ISI:<ut>

Status: checked

=cut
#----------------------------------------------------------------------
sub TabWinHeader($) {
	my ($tabfile) = @_;
	my @fields = ( "PT", "AU", "AF", "TI", "SO", "LA", "DT", "ID",
		"AB", "C1", "RP", "EM", "NR", "TC", "PU", "PI", "PA", "SN",
		"J9", "JI", "PD", "PY", "VL", "IS", "BP", "EP", "DI", "PG",
		"SC", "GA", "UT");

	open (REC, ">>$tabfile") or die "Can't open $tabfile: $!\n";
	foreach $f (@fields) {
		print REC "$f\t";
	}
	print REC "\n";
	close(REC);
}
sub ToTabWin($$) {
	my ($rec, $tabfile) = @_;
	my %data = ();

	%data = XML2Hash($rec);

	open (REC, ">>$tabfile") or die "Can't open $tabfile: $!\n";
	my @fields = ( "PT", "AU", "AF", "TI", "SO", "LA", "DT", "ID",
		"AB", "C1", "RP", "EM", "NR", "TC", "PU", "PI", "PA", "SN",
		"J9", "JI", "PD", "PY", "VL", "IS", "BP", "EP", "DI", "PG",
		"SC", "GA", "UT");

	## foreach $f (@fields) {
	## 	print REC "$f\t";
	## }
	## print REC "\n";

	for ($i=0; $i < $data{"RecCount"}; $i++) {
		foreach $f (@fields) {
			if (defined($data{"$i-$f"})) {
				print REC $data{"$i-$f"} . "\t";
			} else {
				print REC "\t";
			}
		}
		print REC "\n";
	}
	close(REC);
}

#----------------------------------------------------------------------
=head2 SearchRetrieve

Searches and retrieves the full bibliographic records.

	$dbid      DB for the query
	$query     Query in WoS Advanced Search Syntax
	$depth     Time range (e.g. 1900-2008)
	$editions  Databases to search (SCI, AHCI, SSCI, IC, CCR, CPCI)
	           as a space delimited list
	$sort      Field list to sort, prepend with ~ to invert order
	$firstRec  First record to retrieve (counting 1 upwards)
	$numRecs   Number of records to retrieve, < 100
	$fields    The fields to return, empty for "all fields"

	Returns: XML structure containing the bibliographic record, 
			   tagged as ISI record.

TODO  : Handle more than 100 results

Status: checked

=cut
#----------------------------------------------------------------------
sub SearchRetrieve($$$$$$) {
	my ($dbid, $query, $sort, $firstRec, $numRecs, $format) = @_;

	$query = encode("ascii", $query);

	# Base of the REST-URL for searches:
	my $RESTurl = "$WSURL/$SEARCH?prof=$PROF&pwd=$PWD&authType=$AUTHTYPE&ipprof=$IPPROF";

	$RESTurl .= "&query=$query";
	$RESTurl .= "&startrec=$firstRec";
	$RESTurl .= "&numrec=$numRecs";
	$RESTurl .= "&db=$dbid";
	$RESTurl .= "&sort=$sort";
	$RESTurl .= "&format=$format";

	my $ua = new LWP::UserAgent;
	$ua->agent("$useragent");
	$ua->env_proxy;

	my $request   = new HTTP::Request(GET,$RESTurl);
	my $response  = $ua->request($request);
	return($response->content());
}

1;

__END__

