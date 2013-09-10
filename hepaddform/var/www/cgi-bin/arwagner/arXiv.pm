package arXiv;
#=========================================================================
#
#    arXiv.pm
#
#    Simple interface to arXiv.org using their OAI-PHM interface.
#    Instead of fetching dc only use arXiv format
#
#    $Id: $
#    Last change: <Fr, 2012/06/15 11:18:19 cdsware zb0027.zb.kfa-juelich.de>
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
use LWP::Simple;
use XML::XPath;
use IO::Handle;
use locale;
use Encode;

use arwagner::crossref;
use arwagner::arwagner;

*STDOUT->autoflush(1);    # Unbuffered screen IO

@ISA    = ('Exporter');
@EXPORT = qw();

#======================================================================

=head1 NAME

Access for arXiv.org

=cut
#----------------------------------------------------------------------

my $oai             = "http://export.arxiv.org/oai2";
my $oaiGet          = "verb=GetRecord";
my $query           = "identifier=oai:arXiv.org:";
my $metadataprefix  = "metadataPrefix=arXiv";

my $useragent       = "arXiv Client";

#----------------------------------------------------------------------
=head2 

Status: unchecked

=cut
#----------------------------------------------------------------------
sub Fetch ($) {
	my ($identifier) = @_;
	my $url = "$oai?$oaiGet&$metadataprefix&$query$identifier";

	my $ua = new LWP::UserAgent;
	$ua->agent("$useragent");
	$ua->env_proxy;

	my $request   = new HTTP::Request(GET,$url);
	my $response  = $ua->request($request);
	my $xmlresult = $response->content();

	my $xp        = XML::XPath->new(xml=>$xmlresult);
	my $nodeset   = $xp->find('//GetRecord/record/metadata/arXiv');
	my %record    = ();
	my %cxrecord    = ();

	foreach my $node ($nodeset->get_nodelist) {
		$record{SRC}        = "arXiv";
		$record{arXiv}      = $identifier;
		$record{title}      = $node->findvalue('title');
		$record{abstract}   = $node->findvalue('abstract');
		$record{doi}        = $node->findvalue("doi");
		$record{repno}      = $node->findvalue("report-no");
		$record{comments}   = $node->findvalue("comments");
		$record{created}    = $node->findvalue("created");
		$record{updated}    = $node->findvalue("updated");
		$record{categories} = $node->findvalue("categories");

		# Strip linebreaks and normalize spaces
		$record{title}    =~ s/\n/ /g;
		$record{abstract} =~ s/\n/ /g;
		$record{title}    =~ s/\s{1,}/ /g;
		$record{abstract} =~ s/\s{1,}/ /g;
		$record{title}    = arwagner::trim($record{title});
		$record{abstract} = arwagner::trim($record{abstract});


    $subnodes = $node->find('authors/author');
    $record{author}   = "";
    my $i = 0;
    foreach my $aunode ($subnodes->get_nodelist) {
       $al   = $aunode->findvalue("keyname");
       $af   = $aunode->findvalue("forenames");
       $record{surnames}[$i] = $al;
       $record{givennames}[$i] = $af;
			 $record{"AU"} .= $al . ", " . $af. "; ";
       $i++;
    }

		## Usually we'd call crossref here, but in our enrichment logic it is 
		## better to refer crossref resolution to the main module.

		## if (defined($record{doi})) {
		## 	%cxrecord = crossref::DOI2bib($record{doi});
		## 	$record{journal} = $cxrecord{journal};
		## 	$record{volume}  = $cxrecord{volume} ;
		## 	$record{issue}   = $cxrecord{issue}  ;
		## 	$record{page}    = $cxrecord{page}   ;
		## 	$record{bpage}   = $cxrecord{bpage}  ;
		## 	$record{epage}   = $cxrecord{epage}  ;
		## 	$record{pissn}   = $cxrecord{pissn}  ;
		## 	$record{eissn}   = $cxrecord{eissn}  ;
		## 	$record{year}    = $cxrecord{year}  ;
		## }

		## for (my $i=1; $i <= eval($node->find('count(authors/author)'))+1; $i++) {
		## 	$record{surnames}[$i-1]   = $node->findvalue("authors/author[$i]/keyname");
		## 	$record{givennames}[$i-1] = $node->findvalue("authors/author[$i]/forenames");
		## }

		## $record{so} = "";
		## $record{so} .= $record{journal} . ". " if (defined($record{journal}));
		## $record{so} .= $record{year} if (defined($record{year}));
		## $record{so} .= $record{month} . ";" if (defined($record{month}));
		## $record{so} .= " " . $record{volume} if (defined($record{volume}));
		## $record{so} .= "(" . $record{issue} . ")" if (defined($record{issue}));
		## $record{so} .= ":" .$record{page} if (defined($record{page}));

	}
	return(%record);
	#print "$xmlresult";
}

1;

__END__

