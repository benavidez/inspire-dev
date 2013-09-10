package enriche;
#=========================================================================
#
#    enriche.pm
#
#    Try to enrich a bibliographic recrod using calls to external
#    sources
#
#    $Id: $
#    Last change: <Mo, 2012/11/12 15:50:10 cdsware zb0027.zb.kfa-juelich.de>
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

use Exporter;
use vars qw($VERSION @ISA @EXPORT);
$VERSION = "0.01";

use arwagner::crossref;
use arwagner::WoS;
use arwagner::pubmed;
use arwagner::Ebsco;

*STDOUT->autoflush(1);    # Unbuffered screen IO

@ISA    = ('Exporter');
@EXPORT = qw();

#======================================================================

=head1 NAME

Enrich records by calls to external databases

=cut
#----------------------------------------------------------------------
#--------------------------------------------------
# WoS Connection
my $dbid       = "WOS";
my $depth      = "1900-2010";
my $editions   = "SCI AHCI SSCI IC CCR CPCI";
	$editions   = "";					# empty == all subscribed
my $firstRec   = 1;
my $sort       = "Date";
my $numRecs    = 10;
# set times_cited to get this counter set at all
my $fields     = "times_cited get_parent";

	 

#----------------------------------------------------------------------
=head2 getWoS

Provided a ut-code fetch data from Web of Science and return
additional data for the record.

  $ut       : ut-code form WoS

Status: 

=cut
#----------------------------------------------------------------------

sub getWoS($) {
	 my ($ut) = @_;
	
	 my %enrichment = ();

	 # Start on lowest level: WoS
	 if (($ut ne "") and ($ut ne "zs00") and ($ut ne "wos00")) {
			print "      Web of Science ";
			my $query = "ut=($ut)";
			my %wos   = ();

			my $res = WoS::SearchRetrieve($dbid, $query, $depth, $editions, 
   							 $sort, $firstRec, $numRecs, $fields);
			%wos = WoS::XML2Hash($res);
			if ($wos{RecCount} == 1) {
				 
				 $enrichment{ut}       = "" . $wos{"0-UT"} if defined($wos{"0-UT"});
				 $enrichment{lang}     = "" . $wos{"0-LA"} if defined($wos{"0-LA"});
				 $enrichment{abstract} = "" . $wos{"0-AB"} if defined($wos{"0-AB"});
				 $enrichment{wostype}  = "" . $wos{"0-PT"} if defined($wos{"0-PT"});
				 $enrichment{SC}       = "" . $wos{"0-SC"} if defined($wos{"0-SC"});
				 $enrichment{ID}       = "" . $wos{"0-ID"} if defined($wos{"0-ID"});
				 $enrichment{DE}       = "" . $wos{"0-DE"} if defined($wos{"0-DE"});
				 $enrichment{WOSDOI}   = "" . $wos{"0-DI"} if defined($wos{"0-DI"});
				 $enrichment{SRC}      = "Web of Science";

         $enrichment{FundAckTxt}    = $wos{"0-FundAckTxt"} if defined($wos{"0-FundAckTxt"});
         $enrichment{FundingAgency} = $wos{"0-FundingAgency"} if defined($wos{"0-FundingAgency"});
         $enrichment{GrantNo}       = $wos{"0-GrantNo"}    if defined($wos{"0-GrantNo"});
         
				 $enrichment{volume}   = "" . $wos{"0-VL"};##   if ($volume eq "");
				 $enrichment{issue}    = "" . $wos{"0-IS"};##   if ($issue  eq "");
				 $enrichment{page}     = "" . $wos{"0-BP"} . " - " . $wos{"0-EP"}; ## if ($page eq "");
	  		 print "done.\n";
			} else {
	  		 print "N/A.\n";
			}
	 }
	 return(%enrichment)
}

#----------------------------------------------------------------------
=head2 getInspec

provided a DOI search Inspec @EbscoHost to fetch additional data to
enrich the bbibliographic record.

  $doi      : DOI

Status: 

=cut
#----------------------------------------------------------------------
sub getInspec($) {
	 my ($doi) = @_;
	 my %enrichment = ();
	 # higher level: Inspec
	 if ($doi ne "") {
			print "      Inspec ";
			my $dbid      = "inh";
			my $sort      = "date";
			my $firstRec  = "1";
			my $numRecs   = "10";
			my $format    = "brief";
			my $query     = "di+$doi";
			my %inh       = ();

			my $res = Ebsco::SearchRetrieve ($dbid, $query, $sort, 
				 $firstRec, $numRecs, $format);
			%inh = Ebsco::XML2Hash($res);
			if ($inh{RecCount} == 1) {
				 my $value = $inh{"0-ID"};
				 my @headings = split(/\t/, $value);
				 my $i=0;
				 my %uniquehadings = ();
				 foreach my $h (@headings) {
						$uniqueheadings{$h}++;
				 }
				 for my $key (sort(keys %uniqueheadings)) {
				  	push @{$enrichment{InspecKW}}, $key;
				 }

				 %uniqueheadings = ();
				 $value = $inh{"0-SC"};
				 @headings = split(/\t/, $value);
				 $i=0;
				 foreach my $h (@headings) {
						$uniqueheadings{$h}++;
				 }
				 for my $key (sort( keys %uniqueheadings)) {
						push @{$enrichment{InspecSC}}, $key;
				 }
				 $enrichment{inspecid}  = $inh{"0-UT"};
				 $enrichment{abstract}  = $inh{"0-AB"};
				 $enrichment{lang}      = $inh{"0-LA"};
				 $enrichment{volume}    = "" . $inh{"0-VL"} if ($volume ne "");
				 $enrichment{page}      = "" . $inh{"0-BP"} . " - " . $inh{"0-EP"}; ## if ($page eq "");
				 $enrichment{SRC}       = "Inspec, ";
				 print "done.\n";
			} else {
				 print "N/A.\n";
			}
	 }

	 return(%enrichment)
}

#----------------------------------------------------------------------
=head2 getPubmed

provided a DOI search pubmed to fetch additional data to enrich the
bbibliographic record.

  $doi      : DOI

Status: 

=cut
#----------------------------------------------------------------------
sub getPubmed($) {
	 my ($doi) = @_;
	 my %enrichment = ();
	 # higher level: Pubmed
	 if ($doi ne "") {
			print "      Pubmed ";
	  	my %pubmed = ();
	  	@idlist = pubmed::ESearch("Pubmed", $doi);
	  	if ($#idlist == 0) {
	  		 %pubmed = pubmed::EFetch("Pubmed", $idlist[0]);
	  		 $enrichment{abstract}  = $pubmed{abstract};
	  		 $enrichment{lang}      = $pubmed{lang};
				 $enrichment{MeSH}      = $pubmed{MeSH};
	  		 $enrichment{Chemicals} = $pubmed{Chemicals};
	  		 $enrichment{CAS}       = $pubmed{CAS};
	  		 $enrichment{pmid}      = $pubmed{pmid};
	  		 $enrichment{pmc}       = $pubmed{pmc}   if ((defined($pubmed{pmc   })) and ($pubmed{pmc   } ne ""));
				 $enrichment{volume}    = $pubmed{vol}   if ((defined($pubmed{volume})) and ($pubmed{volume} ne ""));
				 $enrichment{issue}     = $pubmed{issue} if ((defined($pubmed{issue })) and ($pubmed{issue } ne ""));
				 $enrichment{page}      = $pubmed{page}  if ((defined($pubmed{page  })) and ($pubmed{page  } ne ""));
				 $enrichment{SRC}       = "Pubmed";
				 print "done.\n";
	  	} else {
				 print "N/A.\n";
			}
	 }

	 return(%enrichment)
}

sub enriche($$) {

	 my ($doi, $ut) = @_;
	 
	 #--------------------------------------------------
	 # Enrich the article by retrieved data.
	 my %enrichment = ();
	 my %enrtmp     = ();

	 $enrichment{ut}      = $ut;
	 $enrichment{doi}     = $doi;
	 %enrtmp = getWoS($ut);
	 while ( my ($key, $value) = each(%enrtmp) ) {
			if ($key ne "SRC") {
				 $enrichment{$key} = $value;
			} else {
				 $enrichment{$key} .= "$value, ";
			}
   }

   if (defined($enrichment{WOSDOI})) {
      if (($doi eq "") and ($enrichment{WOSDOI} ne "")) {
         $doi = $enrichment{WOSDOI};
      }
   }

	 %enrtmp = getPubmed($doi);
	 while ( my ($key, $value) = each(%enrtmp) ) {
			if ($key ne "SRC") {
				 $enrichment{$key} = $value;
			} else {
				 $enrichment{$key} .= "$value, ";
			}
   }

   if (defined($enrichment{lang}) and 
       ($enrichment{lang} =~ m/english/i)) {
     $enrichment{lang} = 'eng';
   }

	 ### %enrtmp = getInspec($doi);
	 ### while ( my ($key, $value) = each(%enrtmp) ) {
	 ###  	if ($key ne "SRC") {
	 ###  		 $enrichment{$key} = $value;
	 ###  	} else {
	 ###  		 $enrichment{$key} .= $value;
	 ###  	}
   ### }

	 # pretty print enrichment sources
	 $enrichment{SRC} =~ s/, $// if defined($enrichment{SRC});

	 return(%enrichment);

}

1;
__END__

