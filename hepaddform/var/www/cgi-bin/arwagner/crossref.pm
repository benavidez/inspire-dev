package crossref;
#=========================================================================
#
#    crossref.pm
#
#    Use crossref to retrieve certain bibliographic data
#
#    $Id: $
#    Last change: <Di, 2013/01/08 15:03:23 cdsware zb0035.zb.kfa-juelich.de>
#    Author     : Alexander Wagner
#    Language   : Perl
#
#-------------------------------------------------------------------------
#
#    Copyright (C) 2009 by Alexander Wagner
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
use IO::Handle;
use arwagner::arwagner;
use locale;
use Encode;

use arwagner::arwagner;

*STDOUT->autoflush(1);    # Unbuffered screen IO

@ISA    = ('Exporter');
@EXPORT = qw();

#======================================================================

=head1 NAME

Access for CrossRef

=cut
#----------------------------------------------------------------------

my $crossrefbase    = "http://doi.crossref.org/servlet/query";
my $crossrefopenurl = "http://www.crossref.org/openurl/";
my $cruser          = "fzjuel";
my $crpass          = "fzjuel1";
my $crformat        = "format=unixref";  # unixref == incl. bibl. data
my $crquery         = "qdata=";
my $crauthortitle   = "type=a";
                   
my $useragent       = "CrossRef Client";

#----------------------------------------------------------------------
=head2 CrossRefQuery

Supply a bibliographic data for CrossRef to get all additional
information available

	$issn     : ISSN
	$journal  : Journal
	$author   : Author
	$vol      : Volume
	$issue    : Issue
	$page     : starting page
	$year     : year
	$type     : document type
	$key      : document ID (DOI)

Status: checked

=cut
#----------------------------------------------------------------------


sub CrossRef2XML($$$$$$$$$) {
	my ($issn, $journal, $author, $vol, $issue, $page, $year, $type, $key) = @_;

	my $query   = "$issn|$journal|$author|$vol|$issue|$page|$year|$type|$key|";
	my $url     = "$crossrefbase?usr=$cruser&pwd=$crpass&$crformat&$crquery$query";

	my $ua = new LWP::UserAgent;
	$ua->agent("$useragent");
	$ua->env_proxy;

	my $request   = new HTTP::Request(GET,$url);
	my $response  = $ua->request($request);
	my $xmlresult = $response->content();

}

#----------------------------------------------------------------------
=head2 CrossRefXML2record

Given the XML result from a CrossRef query return a hash with the
delivered fields

	$xmlresult: Result of the CrossRef query

Status: checked

=cut
#----------------------------------------------------------------------
sub CrossRefXML2record($) {

	my ($xmlresult) = @_;

	my $xp         = XML::XPath->new(xml=>$xmlresult);
	my %record     = ();
	my @surnames   = ();
	my @givennames = ();

  ## print "----------------------------------------------------------------------\n";
  ## print $xmlresult , "\n";
  ## print "----------------------------------------------------------------------\n";
	if ($xmlresult =~ m/journal_metadata/) {
		 # print "This is a journal article.\n";
		 my $nodeset   = $xp->find('//crossref/journal');

		 foreach my $node ($nodeset->get_nodelist) {
			 $record{"SRC"}         = "CrossRef";
			 $record{"journal"}     = "" . $node->findvalue('journal_metadata/full_title');
			 $record{"journalabbr"} = "" . $node->findvalue('journal_metadata/abbrev_title');
			 $record{"pissn"}       = "" . $node->findvalue("journal_metadata/issn[\@media_type='print']");
			 $record{"eissn"}       = "" . $node->findvalue("journal_metadata/issn[\@media_type='electronic']");
       # sometimes cx does not differentiate the ISSNs but stores only
       # one without media type. :S
       if ( ($record{"pissn"} eq "") and ($record{"eissn"} eq "") ) {
          $record{"pissn"}       = "" . $node->findvalue("journal_metadata/issn");
       }
			 $record{"year"}        = "" . $node->findvalue("journal_issue/publication_date[\@media_type='print']/year");
			 $record{"volume"}      = "" . $node->findvalue('journal_issue/journal_volume/volume');
			 $record{"issue"}       = "" . $node->findvalue('journal_issue/issue');
			 $record{"title"}       = "" . $node->findvalue('journal_article/titles/title');
			 # Sometimes crossref returns a lot of linebreaks and spaces.
			 # Strip them of to get a more readable result.
			 $record{"title"} =~ s/\n\r?/ /g;
			 $record{"title"} =~ s/ {1,}/ /g;
			 $record{"title"} = arwagner::trim($record{"title"});
			 $record{"bpage"}       = "" . $node->findvalue('journal_article/pages/first_page');
			 $record{"epage"}       = "" . $node->findvalue('journal_article/pages/last_page');
			 $record{"pages"}        = $record{bpage} . " - " . $record{"epage"};
			 $record{"doi"}         = "" . $node->findvalue('journal_article/doi_data/doi');

			 if ($record{pages} eq " - ") {
				 $record{"pages"} = "" . $node->findvalue('journal_article/publisher_item/item_number');
			   $record{"bpage"}       = $record{"pages"};
			   $record{"epage"}       = "";
			 }

			 my $firstauthor = -1;
			 my $aunodes = $xp->find('//crossref/journal/journal_article/contributors/person_name');
			 my $i = 0;
			 foreach my $aunode ($aunodes->get_nodelist) {
					$surnames       = $aunode->findvalue('surname');
					$givennames     = $aunode->findvalue('given_name');
					$sequence       = $aunode->findvalue('@sequence');
					if ($sequence eq "first") {
				    $record{"firstauthor"} = $surnames . ", " . $givennames;
          }
					$record{"$i-au"}    = $surnames . ", " . $givennames;
					$record{"aunames"} .= $surnames . ", " . $givennames . "; ";
					$i++;
			 }
			 # Add the - in the middle
			 if (($record{"pissn"} ne "") and not ($record{"pissn"} =~ m/-/)) {
				my $i1 = substr($record{pissn}, 0, 4);
				my $i2 = substr($record{pissn}, 4);
				$record{pissn} = "$i1-$i2";
			 }
			 if (($record{"eissn"} ne "") and not ($record{"eissn"} =~ m/-/)) {
				my $i1 = substr($record{eissn}, 0, 4);
				my $i2 = substr($record{eissn}, 4);
				$record{eissn} = "$i1-$i2";
			 }
		 }
	}
	elsif ($xmlresult =~ m/event_metadata/) {
		 # print "This is a conference proceedings article.\n";
		 my $nodeset   = $xp->find('//crossref/conference');
		 foreach my $node ($nodeset->get_nodelist) {

			 $record{"SRC"}         = "CrossRef Conference";
			 $record{"confname"}      = "" . $node->findvalue('event_metadata/conference_name');
			 $record{"conflocation"}  = "" . $node->findvalue('event_metadata/conference_location');

			 $record{"confsday"}      = "" . $node->findvalue('event_metadata/conference_date/@start_day');
			 $record{"confsmonth"}    = "" . $node->findvalue('event_metadata/conference_date/@start_month');
			 $record{"confsyear"}     = "" . $node->findvalue('event_metadata/conference_date/@start_year');
			 $record{"confeday"}      = "" . $node->findvalue('event_metadata/conference_date/@end_day');
			 $record{"confemonth"}    = "" . $node->findvalue('event_metadata/conference_date/@end_month');
			 $record{"confeyear"}     = "" . $node->findvalue('event_metadata/conference_date/@end_year');

			 $record{"proctitle"}     = "" . $node->findvalue('proceedings_metadata/proceedings_title');
			 $record{"publisher"}     = "" . $node->findvalue('proceedings_metadata/publisher');
			 $record{"isbn"}          = "" . $node->findvalue('proceedings_metadata/isbn');

			 $record{"title"}         = "" . $node->findvalue('conference_paper/titles/title');
			 $record{"bpage"}         = "" . $node->findvalue('conference_paper/pages/first_page');
			 $record{"epage"}         = "" . $node->findvalue('conference_paper/pages/last_page');
			 $record{"pages"}         = $record{bpage} . " - " . $record{"epage"};
			 $record{"doi"}           = "" . $node->findvalue('conference_paper/doi_data/doi');
			 $record{"year"}          = "" . $node->findvalue("conference_paper/publication_date[\@media_type='print']/year");
			 $record{"month"}         = "" . $node->findvalue("conference_paper/publication_date[\@media_type='print']/month");

			 my $aunodes = $xp->find('//crossref/conference/conference_paper/contributors/person_name');
			 my $i = 0;
			 foreach my $aunode ($aunodes->get_nodelist) {
					my $surnames        = $aunode->findvalue('surname');
					my $givennames      = $aunode->findvalue('given_name');
					my $sequence        = $aunode->findvalue('@sequence');
					if ($sequence eq "first") {
				    $record{"firstauthor"} = $surnames . ", " . $givennames;
          }
					$record{"$i-au"}    = $surnames . ", " . $givennames;
					$record{"aunames"} .= $surnames . ", " . $givennames. "; ";
					$i++;
			 }
		 }
	} elsif ($xmlresult =~ m/book_metadata/) {
		 # print "This is a book.\n";
		 my $nodeset   = $xp->find('//crossref/book');
		 foreach my $node ($nodeset->get_nodelist) {
			 # Handle the book data
			 $record{"SRC"}         = "CrossRef Book";
			 $record{"bookyear"}      = "" . $node->findvalue("book_metadata/publication_date[\@media_type='print']/year");
			 $record{"bookpublisher"} = "" . $node->findvalue('book_metadata/publisher/publisher_name');
			 $record{"bookpubplace"}  = "" . $node->findvalue('book_metadata/publisher/publisher_place');
			 $record{"bookdoi"}       = "" . $node->findvalue('book_metadata/doi_data/doi');

			 # there might be multiples!
			 $record{"booktitle"}     = "" . $node->findvalue('book_metadata/titles/title');
			 $record{"bookpisbn"}     = "" . $node->findvalue("book_metadata/isbn[\@media_type='print']");
			 $record{"bookeisbn"}     = "" . $node->findvalue("book_metadata/isbn[\@media_type='electronic']");

			 my $aunodes = $xp->find('//crossref/book_metadata/contributors/person_name');
			 my $i = 0;
			 foreach my $aunode ($aunodes->get_nodelist) {
					my $surnames     = $aunode->findvalue('surname');
					my $givennames   = $aunode->findvalue('given_name');
					my $role         = $aunode->findvalue('@contributor_role');
					if ($sequence eq "first") {
				    $record{"firstauthor"} = $surnames . ", " . $givennames;
          }
					$record{"$i-book" . "-" . $role} = $surnames . ", " . $givennames;
					$i++;
			 }

			 # now the item requested (chapter etc.)

			 $record{"comptype"}      = "" . $node->findvalue('content_item/@component_type');
			 $record{"compnumber"}    = "" . $node->findvalue('content_item/component_number');

			 $record{"bpage"}         = "" . $node->findvalue('content_item/pages/first_page');
			 $record{"epage"}         = "" . $node->findvalue('content_item/pages/last_page');
			 $record{"pages"}         = $record{"bpage"} . " - " . $record{"epage"};
			 $record{"doi"}           = "" . $node->findvalue('content_item/doi_data/doi');
			 $record{"title"}         = "" . $node->findvalue('content_item/titles/title');

			 $aunodes = $xp->find('//crossref/conference/conference_paper/contributors/person_name');
			 $i = 0;
			 foreach my $aunode ($aunodes->get_nodelist) {
					my $surnames           = $aunode->findvalue('surname');
					my $givennames         = $node->findvalue('given_name');
					my $sequence           = $node->findvalue('@sequence');
					if ($sequence eq "first") {
				    $record{"firstauthor"} = $surnames . ", " . $givennames;
          }
					$record{"$i-au"}    = $surnames . ", " . $givennames;
					$record{"aunames"} .= $surnames . ", " . $givennames. "; ";
					$i++;
			 }
		 }
	}
  for my $k (keys(%record)) {
    $record{$k} = arwagner::trim($record{$k});
  }
	return(%record)
}

#----------------------------------------------------------------------
=head2 CrossRefQuery

Status: checked

=cut
#----------------------------------------------------------------------
sub CrossRefQuery($$$$$$$$$) {
	my ($issn, $journal, $author, $vol, $issue, $page, $year, $type, $key) = @_;
	### print ("$issn, $journal, $author, $vol, $issue, $page, $year, $type, $key");
	my $xml = CrossRef2XML($issn, $journal, $author, $vol, $issue, $page, $year, $type, $key);
	return (CrossRefXML2record($xml));
}


#----------------------------------------------------------------------
=head2 DOI2XML

Given a DOI generate suitable metadata if CrossRef knows the DOI.

	$doi  = DOI of the document

Status: checked

=cut
#----------------------------------------------------------------------
sub DOI2xml($) {
	my ($doi)  = @_;
	my $ua = new LWP::UserAgent;
	$ua->agent("$useragent");
	$ua->env_proxy;
	my $url  = "$crossrefbase?pid=$cruser:$crpass&format=unixref&id=$doi";
  # print "$url\n\n";
	my $request   = new HTTP::Request(GET,$url);
	my $response  = $ua->request($request);
	my $xml       = $response->content();
	return($xml);
}

#----------------------------------------------------------------------
=head2 DOI2Bib

Return a hash with the bibliographic data for a given DOI

	$doi : DOI of the document

Status: checked

=cut
#----------------------------------------------------------------------
sub DOI2bib($) {
	my ($doi)  = @_;
	my $xmlresult = DOI2xml($doi);
	my %record = CrossRefXML2record($xmlresult);
	return(%record);
}

sub AuTit2XML($$) {
	my ($author, $title)  = @_;
	$title =~ s/ /+/g;

	my $ua = new LWP::UserAgent;
	$ua->agent("$useragent");
	$ua->env_proxy;
	my $url     = "$crossrefbase?usr=$cruser&pwd=$crpass&$crauthortitle&$crformat&$crquery$title|$author||key|";

	my $request   = new HTTP::Request(GET,$url);
	my $response  = $ua->request($request);
	return($response->content());
}


sub AuTit2Bib($$) {
	my ($author, $title)  = @_;

	my $xmlresult = AuTit2XML($author, $title);
	my %record = CrossRefXML2record($xmlresult);
	
	return(%record);
}

1;

__END__

