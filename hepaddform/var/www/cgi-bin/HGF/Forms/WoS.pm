package WoS;
#=========================================================================
#
#    WoS.pm
#
#    http://scientific.thomson.com/support/faq/webservices/
#
#    Module to access the Web of Science / Web of Knowledge from Perl
#    by means of the WoS Web Service.
#
#    $Id: $
#    Last change: <Fr, 2012/11/09 14:56:10 cdsware zb0027.zb.kfa-juelich.de>
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

use DBI;
use XML::XPath;
use Encode;
use IO::Handle;
use HGF::Forms::HGF;
use FindBin;

*STDOUT->autoflush(1);    # Unbuffered screen IO

@ISA    = ('Exporter');
@EXPORT = qw();

#======================================================================

my $dumpstart    = 100;
# If more than $dumpstart results are retrieved, store them on disk
# while processing
my $tempdumpfile = "wosdmp.xml";
#======================================================================
=head1 NAME

WoS - routines for WoS applications. A documentation of the Web
Service can be found in the documents

		ESTI SOAP API Search Service
		Web of Science Search Retrieve Codes and Descriptions

from Thomson Scientific.
=cut
#----------------------------------------------------------------------

#----------------------------------------------------------------------
=head2 DumpRec

Dumps the record passed to an external file.

	$rec     : the record to dump
	$recfile : the file to use

Status: checked

=cut
#----------------------------------------------------------------------
sub DumpRec($$) {

	my ($rec, $recfile) = @_;

	open (REC, ">$recfile") or die "Can't open $recfile: $!\n";
	print REC '<?xml version="1.0" encoding="ISO-8859-1"?>' . "\n";
	print REC "$rec\n";
	close(REC);
}

#----------------------------------------------------------------------
=head2 XML2Hash

Extracts fields from an XML structure ot a hash tagged with the usual
2 char WoS tags.

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
	my %data  = ();

	# Check, if at least one record was retrieved, otherwise xpath is
	# not happy...
	if ($rec =~ /\<REC /) {
		my $xmlxpath = XML::XPath->new(xml=>$rec);
		my $REC = $xmlxpath->find("//REC");
		my $rno = 0;
		foreach $entry ($REC->get_nodelist) {
			$data{"$rno-SRC"} = "Web of Science";
			$data{"$rno-DT"}  = "" . $entry->find('item/doctype');
			$data{"$rno-UT"}  = "WOS:" . $entry->find('item/ut');
			$data{"$rno-TI"}  = "" . $entry->find('item/item_title');
			$data{"$rno-SO"}  = "" . $entry->find('item/source_title');
			$data{"$rno-J9"}  = "" . $entry->find('item/source_abbrev');

			$data{"$rno-LA"}  = "" . $entry->find('item/languages/primarylang');
			$data{"$rno-AB"}  = "" . $entry->find('item/abstract[@avail="Y"]/p');
			$data{"$rno-RP"}  = "" . $entry->find('item/reprint/rp_author');
			$data{"$rno-RP"} .= ", " . $entry->find('item/reprint/rp_address') . ".";
			$data{"$rno-PY"}  = "" . $entry->find('item/bib_issue/@year');
			$data{"$rno-VL"}  = "" . $entry->find('item/bib_issue/@vol');
			$data{"$rno-BP"}  = "" . $entry->find('item/bib_pages/@begin');
			$data{"$rno-EP"}  = "" . $entry->find('item/bib_pages/@end');
			$data{"$rno-PG"}  = "" . $entry->find('item/bib_pages/@pages');
			$data{"$rno-NR"}  = "" . $entry->find('item/refs/@count');
			$data{"$rno-TC"}  = "" . $entry->find('./@timescited');

			$data{"$rno-CK"}  = "" . $entry->find('item/i_ckey');
			
			$data{"$rno-IS"}  = "" . $entry->find('issue/bib_vol/@issue');
			$data{"$rno-PU"}  = "" . $entry->find('issue/copyright/publisher');
			$data{"$rno-PA"}  = "" . $entry->find('issue/copyright/pub_address');
			$data{"$rno-PI"}  = "" . $entry->find('issue/copyright/pub_city');
			$data{"$rno-SN"}  = "" . $entry->find('issue/issn');
			$data{"$rno-JI"}  = "" . $entry->find('issue/abbrev_iso');
			$data{"$rno-PD"}  = "" . $entry->find('issue/bib_date/@date');
			$data{"$rno-PT"}  = "" . $entry->find('issue/pubtype/@code');
			$data{"$rno-GA"}  = "" . $entry->find('issue/ids');

			$au = "";
			$af = "";
			$au .= $entry->find("item/authors/primaryauthor");
			$au .= "; ";

      # we always have this
      my $subnodes = $entry->find('item/authors/author');
      foreach my $aunode ($subnodes->get_nodelist) {
          $au .= $aunode->findvalue('.') . "; ";
      }
			$data{"$rno-AU"} = $au;
			$data{"$rno-AF"} = $af;

      # and sometimes it gets better
      $subnodes = $entry->find('item/authors/fullauthorname');
			my @audta = ();
      my $i = 0;
      foreach my $aunode ($subnodes->get_nodelist) {
         $al   = $aunode->findvalue("AuLastName");
         $af   = $aunode->findvalue("AuFirstName");
         $ac   = $aunode->findvalue("AuCollectiveName");

         @aa   = ();
         for (my $j=1; $j <= $aunode->find("count(address)"); $j++) {
            push @{$data{"$rno-AuAddress"}[$i]}, $aunode->find("address[$j]");
         }
			 	 $data{"$rno-AuthorLastName"}[$i]       = $al;
			 	 $data{"$rno-AuthorFirstName"}[$i]      = $af;
			 	 $data{"$rno-AuthorCollectiveName"}[$i] = $ac;
         $i++;
      }

			# Subject categories
			$sc = "";
			for (my $i=1; $i <= $entry->find('count(categories/category)'); $i++) {
				$sc .= $entry->find("categories/category[$i]") . "; ";
			}
			$data{"$rno-SC"} = $sc;

			# Extract funding
      $data{"$rno-FundAckTxt"} = $entry->find('item/fund_ack/fund_text/p');
			$data{"$rno-Funding"} = ();
      
      $i = 0;
      $grantnodes = $entry->find('item/fund_ack/grant');
      foreach my $gnode ($grantnodes->get_nodelist) {
				$data{"$rno-FundingAgency"}[$i]= "". $gnode->find("fund_org");

        $ggnodes = $gnode->find('fund_grants/fund_grant');
        foreach my $gg ($ggnodes->get_nodelist) {
          my $g = $gg->find('.');
					$data{"$rno-GrantNo"}[$i] .= "$g\t";
        }
        $i++;
      }

			# Keywords Plus
			$kw = "";
			for (my $i=1; $i <= $entry->find('count(item/keywords_plus/keyword)'); $i++) {
				$kw .= $entry->find("item/keywords_plus/keyword[$i]") . "; ";
			}
			$data{"$rno-ID"} = $kw;

			$kw = "";
			for (my $i=1; $i <= $entry->find('count(item/keywords/keyword)'); $i++) {
				$kw .= $entry->find("item/keywords/keyword[$i]") . "; ";
			}
			$data{"$rno-DE"} = $kw;

			$c1 = "";
			for (my $i=1; $i <= $entry->find('count(item/research_addrs/research)'); $i++) {
				$c1 .= $entry->find("item/research_addrs/research[$i]/rs_address") . ".; ";
			}
			$data{"$rno-C1"} = $c1;

			$em = "";
			for (my $i=1; $i <= $entry->find('count(item/emails/email)'); $i++) {
				$em .= '"' . $entry->find("item/emails/email[$i]/name") . '" ';
				$em .= "<" . $entry->find("item/emails/email[$i]/email_addr") . ">; ";
			}
			$data{"$rno-EM"}  = $em;

##--##		$cr = "";
##--##		for (my $i=1; $i <= $entry->find('count(item/refs/ref)'); $i++) {
##--##			$cr .= $entry->find("item/refs/ref[$i]") . '; ';
##--##		}
##--##		$data{"$rno-CR"}  = $cr;

			$an = "";
			for (my $i=1; $i <= $entry->find('count(item/article_nos/article_no)'); $i++) {
				$an = "" . $entry->find("item/article_nos/article_no[$i]");
				if ($an =~ /DOI/) {
					$an =~ s/DOI //g;
					$data{"$rno-DI"} = $an
				}
			}

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
=head2 ParseRetrieve

Dessects the XML result from usual Retrieve queries like

	retrieve          (retrieveReturn)
	citedReferences   (citedReferencesReturn)

	$result : the raw XML from the query
	$resnode: Then node above the actual data (see WSDL)

Status: checked

=cut
#----------------------------------------------------------------------
sub ParseRetrieve($$) {

	my ($result, $resnode) = @_;

	my $xmlxpath = XML::XPath->new(xml=>$result);
	my $records = $xmlxpath->find("//$resnode");

	return($records);
}

#----------------------------------------------------------------------
=head2 SearchRetrieve

  Call a very simplified python stub for the actual interaction with
  the new WOS service.

  TODO all this needs to be properly recoded in python

	$query     Query in WoS Advanced Search Syntax

	Returns: XML structure containing the bibliographic record, 
			   tagged as ISI record.

Status: checked

=cut
#----------------------------------------------------------------------
sub SearchRetrieve($$$$$$$$) {
	my ($dbid, $query, $depth, $editions,
		 $sort, $firstRec, $numRecs, $fields) = @_;

	# WoS requires 7bit
	$query = encode("ascii", $query);

	# get the the given number of records

  # we need to find where we are to get the proper path for our
  # fetcher. 
  # TODO all this is ugly 
  my $path = $FindBin::Bin;
  my $res = `/usr/bin/env python $path/HGF/Forms/wosfetch.py '$query'`;
	return($res);
}


1;

__END__

