#!/usr/bin/perl -w
#=========================================================================
#
#    GenMetadata.pl
#
#    Try to fetch as much metadata as possible given an unique identifier. 
#    Hook up with:
#
#    doi : CrossRef, Inspec, Pubmed
#    pmid: Pubmed
#    ut  : Web of Science
#    issn: Invenio for ZDBID
#
#    $Id: $
#    Last change: <Do, 2012/11/08 15:26:22 cdsware zb0027.zb.kfa-juelich.de>
#    Author     : Alexander Wagner
#    Language   : Perl
#
#-------------------------------------------------------------------------
#
#    Copyright (C) 2011, 2012 by Alexander Wagner
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
use Sys::Hostname;

use File::Basename;
use File::Path;
# use lib '/usr/share/perl/5.10.1/CPAN';
use lib (&fileparse($0))[1].".";
use Encode;
use IO::Handle;
use LWP::UserAgent;
use JSON;
use Sys::Hostname;
use Data::Dumper;

# Some local stuff
use HGF::Forms::HGF;
use HGF::Forms::CGIHelper;
use HGF::Forms::MarcXML;
use HGF::Forms::arXiv;
use HGF::Forms::crossref;
use HGF::Forms::Ebsco;
use HGF::Forms::GVK;
use HGF::Forms::pubmed;
use HGF::Forms::WoS;
use HGF::Forms::inspire;

use CGI qw(-utf8);
### use CGI qw/ -oldstyle_urls/;
### $CGI::USE_PARAM_SEMICOLONS = 0; # Same as oldstyle_urls


#--------------------------------------------------
# Input identifiers
my $doi    = "";
my $pmid   = "";
my $ut     = "";
my $arXiv  = "";
my $inspire ="";
my $issn   = "";
my $ppn    = "";
my $isbn   = "";
my $wwwhost= "";


# Mode full is slow, so for interactive use use "quick" which just asks
# crossref (slow enough)
my $mode   = "full";
#$mode = "quick";

my $format = "Marc";

# By default do not fetch reference list if a UT code is present as this is
# very time consuming. This should be done only in an offline enrichment
# process!
my $fetchReferenceList = 0;

my $useragent          = "Mozilla/5.0 (X11; U; Linux amd64; rv:5.0) Gecko/20100101 Firefox/5.0 (Debian)";

#--------------------------------------------------
# Record contains the enriched record as a hash.
# The source BEST MATCH refers to usage of the most reliable source.
# In ascending order quality is given by:
#    WoS -> CrossRef -> Pubmed, Inspec
# 
# TODO Author affiliations in case WoS Author information is available?
#      Downside: WoS author information is pretty bad.
# TODO Author Handling: Pubmed returns First/Lastname, WoS does sometimes,
#                       Inspec only the full name(?)
#
# BEST MATCH    : au     
# BEST MATCH    : abstract  
# BEST MATCH    : issn      
# BEST MATCH    : issue     
# BEST MATCH    : journal   
# BEST MATCH    : lang      
# BEST MATCH    : page      
# BEST MATCH    : title     
# BEST MATCH    : volume    
# BEST MATCH    : year      
# crossref      : aunames   
# crossref      : doi       
# crossref      : eissn     
# crossref      : pissn     
# crossref      : confname
# crossref      : conflocation
# crossref      : confdates
# crossref      : proctitle
# crossref      : procpublisher
# crossref      : procisbn
# inspec        : inspecid  
# inspec        : InspecKW      (@array)
# inspec        : InspecSC      (@array)
# pubmed        : CAS           (@array)
# pubmed        : Chemicals     (@array)
# pubmed        : MeSH          (@array)
# pubmed        : pmc       
# pubmed        : pmid      
# wos           : DE        
# wos           : ID        
# wos           : SC        
# wos           : ut        
# wos           : wostype   
# wos           : FundingAgency (@array)
# wos           : GrantNo       (@array)
# wos           : ReferenceList (@array)
my %record = ();

#--------------------------------------------------
# URL to handle PMC identifiers
my $pmcprefix  = "http://www.ncbi.nlm.nih.gov/pmc/articles";

#--------------------------------------------------
# Inspec connection parameters for Ebsco Host Search API
my $inhdbid      = "inh";
my $inhsort      = "date";
my $inhfirstRec  = "1";
my $inhnumRecs   = "10";
my $inhformat    = "brief";

#--------------------------------------------------
# WoS connection parameters
my $dbid       = "WOS";
my $depth      = "";        # empty == all times
my $editions   = "";	      # empty == all subscribed
my $firstRec   = 1;
my $sort       = "Date";
my $numRecs    = 10;
# set times_cited to get this counter set at all
my $fields     = "times_cited get_parent";

#--------------------------------------------------
my $gbvsru     = PICA::Source->new( SRU => "http://gso.gbv.de/sru/DB=2.1/" );
my $gbvunapi   = "http://unapi.gbv.de/?format=pp&id=gvk:ppn:"; # . $ppn

#--------------------------------------------------
my ($inveniojournalid, $zdbid, $jtitle, $issnlst, $idlst) = "";

#--------------------------------------------------
# Collect records fist then build up the overwriting
my %cxrec      = ();  # Results from CrossRef
my %inhrec     = ();  # Results from Inspec
my %pmrec      = ();  # Results from PubMed
my %arxivrec   = ();  # Results from arXiv
my %inspirerec = ();  # Results from INSPIRE
my %wosrec     = ();  # Results from WoS
my %bookrec    = ();  # Results from GVK
my %jrecord    = ();  # Results from Invenio (Journal data)

my @CK     = (); # Contain CK codes with the references in an article
		 # Retrieval of the bibliogrpahic data to this is pretty
		 # time consuming, has to be done offline!

#----------------------------------------------------------------------
# Start with worst identifiers first and hope to get better ones. In case,
# set DOI and so on to get maximum enrichment.
sub FetchWoSReferences($) {
	my ($ut) = @_;
	my $refxml = "";
	### print "Extracting references from WoS...\n";
	# Get a list of ck-codes containing the references of the article
	$ut =~ s/WOS://;
	$ut =~ s/ISI://;
	### print "$ut\n";
	@CK = WoS::CitedReferences($dbid, $ut);
	my $i = 0;
	foreach my $ck (@CK) {
		### print "   $ck\n";
		my $query = "CK=($ck)";
		my $res = WoS::SearchRetrieve($dbid, $query, $depth, $editions, 
									$sort, $firstRec, $numRecs, $fields);
		my %wosrec = WoS::XML2Hash($res);
		my $ut       = $wosrec{"0-UT"};
		$ut =~ s/WOS://;
		$ut =~ s/ISI://;

		## # Construct the URL via output format.
		## # Adopt bfe_references.py to use this field
		## #
		## ### my $wosurl   = "http://gateway.isiknowledge.com/gateway/Gateway.cgi";
		## ### $wosurl     .= "?GWVersion=2";
		## ### $wosurl     .= "&SrcApp=WEB";
		## ### $wosurl     .= "&SrcAuth=HSB";
		## ### $wosurl     .= "&DestApp=WOS";
		## ### $wosurl     .= "&DestLinkType=FullRecord";
		## ### $wosurl     .= "&KeyUT=$ut";
		my $citation = $wosrec{"0-SO"} . ", "  . $wosrec{"0-VL"} . ", " .
								  $wosrec{"0-IS"} . ", (" . $wosrec{"0-PY"} . "), ".
									$wosrec{"0-BP"} . " - " . $wosrec{"0-EP"};
		              
		my %marcdta = ();
		$i++;
		$marcdta{a} = $wosrec{"0-DI"};
		$marcdta{m} = $wosrec{"0-AU"} . ' : ' . $wosrec{"0-TI"};
		$marcdta{v} = $wosrec{"0-VL"};
		$marcdta{n} = $wosrec{"0-IS"};
		$marcdta{y} = $wosrec{"0-PY"};
		$marcdta{p} = $wosrec{"0-BP"} . " - " . $wosrec{"0-EP"};
		$marcdta{s} = $citation;
		$marcdta{t} = $wosrec{"0-SO"};
		$marcdta{u} = $wosrec{"0-UT"};
	  $refxml .= MarcXML::MarcField("999", "C", "5", %marcdta);
	}
	return($refxml);
}

#----------------------------------------------------------------------

sub FetchGVK($) {
	my ($ppn) = @_;
	# If we have a ppn we get exatly one match, so this is easy. If we
	# have only an ISBN number we get multiple matches, the user has to
	# select from a list what's the proper entity.
	if ($ppn ne "") {
		%bookrec = GVK::FetchPPN($ppn);
	}
}

#----------------------------------------------------------------------
sub FetchUT($$$) {
	my ($ut, $doi, $fetchReferenceList) = @_;
	my $wosdoi = ""; # DOIs from WoS are not realiable :S

	if (defined($ut) and ($ut ne "")) {
			# A WoS UT code was passed on, this should triger:
			#   - Call of WoS to get publication data
			#   - Try to get DOI from WoS, if available:
			#     * Verify DOI by CrossRef call and pass it onwards

			my $query = "ut=($ut)";
			my $res = WoS::SearchRetrieve($dbid, $query, $depth, $editions, 
   							$sort, $firstRec, $numRecs, $fields);
			%wosrec = WoS::XML2Hash($res);
			$wosrec{WOSDOI} = $wosrec{"0-DI"};

			#---------- CrossRef
			if (defined($wosrec{WOSDOI})) {
				my %cxrec = crossref::DOI2bib($wosrec{WOSDOI});
				$wosdoi = $cxrec{doi} if (defined($cxrec{doi}));
		 }
	}
	return($wosdoi);
}

#----------------------------------------------------------------------
sub FetchPMID($) {
	my ($pmid) = @_;

	if (defined($pmid) and ($pmid ne "")) {
			# A PMID was passed on, this should trigger:
			#   - Pubmed lookup to get publication data, indexing and DOI
			#   Proceed with DOI set

			%pmrec = pubmed::EFetch("Pubmed", $pmid);
			$doi = $pmrec{doi} if defined($pmrec{doi});
	}
}

#----------------------------------------------------------------------
sub FetchDOI($) {
	my ($doi) = @_;

	if ($doi ne "") {
		# A DOI was passed on, this should trigger:
		#   - CrossRef lookup for publication data
		#   - Inspec lookup to get indexing and inh-ID
		#   - Pubmed lookup to get indexing and PMID
		
		#---------- CrossRef
		%cxrec = crossref::DOI2bib($doi);

		if ($mode ne "fast") {
			#---------- Inspec
			my $inhquery = "DI+$doi";
			my $res = Ebsco::SearchRetrieve($inhdbid, $inhquery, 
											$inhsort, $inhfirstRec, $inhnumRecs, $inhformat);
			%inhrec = Ebsco::XML2Hash($res);

			#---------- Pubmed
			my @idlist = pubmed::ESearch("Pubmed", $doi);
			if ($#idlist == 0) {
					%pmrec = pubmed::EFetch("Pubmed", $idlist[0]);
			}
		}
	}
}

#----------------------------------------------------------------------
sub FetchArXiv($) {
	my ($id) = @_;

	if (defined($id) and ($id ne "")) {
		$id =~ s/arXiv://g;
		%arxivrec = arXiv::Fetch($id);
		$doi = $arxivrec{doi};

		if ($mode eq "full") {
			#---------- Inspec
			my $inhquery = "di+$doi";
			my $res = Ebsco::SearchRetrieve($inhdbid, $inhquery, 
											$inhsort, $inhfirstRec, $inhnumRecs, $inhformat);
			%inhrec = Ebsco::XML2Hash($res);

			#---------- Pubmed
			# There might be hits from the biology part of arXiv
			my @idlist = pubmed::ESearch("Pubmed", $doi);
			if ($#idlist == 0) {
					%pmrec = pubmed::EFetch("Pubmed", $idlist[0]);
			}
		}
	}
}

sub FetchInspire($) {
	my ($id) = @_;

	if (defined($id) and ($id ne "")) {
		$id =~ s/inspire://gi;
		%inspirerec = inspire::Fetch($id);
		$doi = $inspirerec{doi};

		if ($mode eq "full") {
			#---------- Inspec
			my $inhquery = "di+$doi";
			my $res = Ebsco::SearchRetrieve($inhdbid, $inhquery, 
							$inhsort, $inhfirstRec, $inhnumRecs, $inhformat);
			%inhrec = Ebsco::XML2Hash($res);

			#---------- Pubmed
			# There might be hits from the biology part of INSPIRE
			my @idlist = pubmed::ESearch("Pubmed", $doi);
			if ($#idlist == 0) {
					%pmrec = pubmed::EFetch("Pubmed", $idlist[0]);
			}
		}
	}
}


#----------------------------------------------------------------------
sub FetchData($$$$$$) {
	my ($doi, $pmid, $ut, $arxiv, $issn, $inspire) = @_;

  my $wosdoi = FetchUT($ut, $doi, 1) if (defined($ut));
	FetchArXiv($arxiv)                 if (defined($arxiv));
	FetchInspire($inspire)             if (defined($inspire));
	FetchPMID($pmid)                   if (defined($pmid));
	if (defined($doi) and ($doi ne "")) {
			FetchDOI($doi);
	}
	elsif (defined($wosdoi) and ($wosdoi ne "")) {
			FetchDOI($wosdoi);
	}
	%jrecord = CGIHelper::FetchISSN($issn) if (defined($issn));
}

#======================================================================

my $debug =  0;
$doi = "10.1109/eScience.2010.42";     # Proceedings
$doi = "10.1007/978-1-4419-1719-5_12"; # Book
$doi = "10.1103/PhysRev.47.777";       # Journal article

$doi  = "10.1016/j.bpj.2010.06.068";
$doi  = "10.1140/epjc/s10052-007-0279-6";
$ppn  = "629686653";
$isbn = "978-3-642-12893-6";
# $pmid = "20923669";
# $ut   = "000282850600040";
# $issn = "0006-3495";
# $arXiv= "arXiv:hep-ph/0608065";
# $inspire = "inspire:858508";

my $q = new CGI;

## print $q->header(-type=>'text/plain', -charset=>"utf-8");

# # Fetch only valid parameters, ignore all the rest.
if ($debug == 0 ) {
   $wwwhost= $q->param("wwwhost");

	 $doi    = $q->param("doi");
	 $pmid   = $q->param("pmid");

	 # Handle several prefixes for WOS
	 $ut     = $q->param("ut")  if (defined($q->param("ut")));
	 $ut     = $q->param("wos") if (defined($q->param("wos")));
	 $ut     = $q->param("isi") if (defined($q->param("isi")));

	 $arXiv  = $q->param("arxiv");
	 $inspire = $q->param("inspire");
	 $ppn    = $q->param("ppn");
	 $isbn   = $q->param("isbn");
	 $issn   = $q->param("issn");
	 $mode   = $q->param("mode");
	 $format = $q->param("format");
} else {
	$mode = "full";
}

$wwwhost= hostname if (not(defined($wwwhost)));
$doi    = "" if (not(defined($doi)));
$pmid   = "" if (not(defined($pmid)));
$ut     = "" if (not(defined($ut)));
$arXiv  = "" if (not(defined($arXiv)));
$issn   = "" if (not(defined($issn)));
$ppn    = "" if (not(defined($ppn)));
$isbn   = "" if (not(defined($isbn)));
$mode   = "full" if (not(defined($mode)));
$format = "JSON" if (not(defined($format)));

CGIHelper::SetFormat($format);
CGIHelper::SetWWWHost($wwwhost);

my $dataoutput = "";

if (($mode eq "full") or ($mode eq "thin")) {
	# print "Fetching $doi, $pmid, $ut, $arXiv, $issn\n";
	FetchData($doi, $pmid, $ut, $arXiv, $issn,$inspire);
} 
if ($mode eq "fast") {
	if ($ut ne "") {
		FetchUT($ut, "", 0);
	}
	elsif ($ppn ne "") {
		FetchGVK($ppn);
	}
	elsif ($pmid ne "") {
		FetchPMID($pmid);
		$doi = $pmrec{doi} if (defined($pmrec{doi}));
	}
	elsif ($arXiv ne "") {
		FetchArXiv($arXiv);
		$doi = $arxivrec{doi} if (defined($arxivrec{doi}));
	}
	elsif ($inspire ne "") {
		FetchInspire($inspire);
		$doi = $inspirerec{doi} if (defined($inspirerec{doi}));
	}
	
}

# Allways try to call CrossRef at last, as we might have 
# won a DOI in some of the former calls 
if (defined($doi)) {
	# print "Fetching doi: $doi\n";
	FetchDOI($doi);
}
# If we don't have an ISSN, did we win one? If so use it!
if ((not(defined($issn))) or ($issn eq "")) {
	if (defined($wosrec{"0-SN"})) {
		if ($wosrec{"0-SN"} ne "") {
			$issn = $wosrec{"0-SN"};
		} 
	} 
	if (defined($inhrec{"0-SN"})) {
		if ($inhrec{"0-SN"} ne "") {
			 $issn = $inhrec{"0-SN"};
		}
	}
	if (defined($pmrec{"issn"})) {
		if ($pmrec{"issn"} ne "") {
			$issn = $pmrec{"issn"};
		}
	}
	if (defined($cxrec{pissn})) {
		if ($cxrec{pissn} ne "") {
			$issn = $cxrec{pissn}
		}
	}
	if ((defined($cxrec{eissn}))) {
		if ($cxrec{eissn} ne "") {
			$issn = $cxrec{eissn}
		}
	}
}

# Allways try to fetch Journal informations. 
# This is a cheap call as it is resolved locally.
# print "Fetching journal: $issn\n";
if (defined($issn) and ($issn ne '')) {
   %jrecord = CGIHelper::FetchISSN($issn);
}
elsif (defined($wosrec{"0-SO"})) {
   # we have no ISSN but a WOS journal name.  This happens from the
   # LITE search in WOS which is indeed very LITE with it's returns.
   # However we can prefix this Name by WOS: and should find it in our
   # journals collection in 0247_a
   my $wosjournal = "WOS:" . $wosrec{"0-SO"};
   %jrecord = CGIHelper::FetchByName($wosjournal);
}

%record = CGIHelper::ConstructRecord(
			$mode,
			\%cxrec,  \%inhrec,  \%pmrec,  \%arxivrec, 
			\%wosrec, \%bookrec, \%jrecord, \%inspirerec
);
$dataoutput = CGIHelper::MakeOutput($format, $mode, %record);
# binmode STDOUT, ":utf8";
$dataoutput = encode('utf-8', NFC $dataoutput);
print $dataoutput;

