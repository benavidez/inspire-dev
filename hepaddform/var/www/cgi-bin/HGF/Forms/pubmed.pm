package pubmed;
#=========================================================================
#
#    pubmed.pm
#
#    Simple interface to NCBI Pubmed via Entrez
#
#    $Id: $
#    Last change: <Mo, 2012/07/30 09:09:05 cdsware zb0027.zb.kfa-juelich.de>
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

use HGF::Forms::HGF;

*STDOUT->autoflush(1);    # Unbuffered screen IO

@ISA    = ('Exporter');
@EXPORT = qw();

#======================================================================

=head1 NAME

Access for CrossRef

=cut
#----------------------------------------------------------------------

my $eutils          = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils";
my $esearch         = "esearch.fcgi"; # ?db=<DB>&term=<query>";
my $efetch          = "efetch.fcgi";  # ?db=<DB>&id=<pmid-lst>&rettype=<type>&retmode=<mode>"
my $db              = "Pubmed";

my $useragent       = "Pubmed Client";

#----------------------------------------------------------------------
=head2 

Status: unchecked

=cut
#----------------------------------------------------------------------
#http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=Pubmed&term=science[journal]+AND+breast+cancer+AND+2008[pdat]
sub ESearch ($$) {
	my ($db, $query) = @_;
	my $url = "$eutils/$esearch?db=$db&term=$query";
	# print "$url\n";

	my $ua = new LWP::UserAgent;
	$ua->agent("$useragent");
	$ua->env_proxy;

	my $request   = new HTTP::Request(GET,$url);
	my $response  = $ua->request($request);
	my $xmlresult = $response->content();
  $xmlresult =~ s/<!DOCTYPE.*//;

	my $xp        = XML::XPath->new(xml=>$xmlresult);
	my $nodeset   = $xp->find('/');

	my @idlist    = ();
	my $i         = 0;
	
	foreach my $node ($nodeset->get_nodelist) {
		for (my $i=1; $i <= eval($node->find('count(//IdList/Id)')); $i++) {
			$idlist[$i-1] = $node->findvalue("//IdList/Id[$i]");
		}
	}

	return(@idlist);
}
# http://eutils.ncbi.nlm.nih.gov/entrez/eutils//efetch.fcgi?db=Pubmed&id=19008416&rettype=xml
sub EFetch ($$) {
	my ($db, $idlist) = @_;
	my $url = "$eutils/$efetch?db=$db&id=$idlist&rettype=xml";
	#print "$url\n";

	my $ua = new LWP::UserAgent;
	$ua->agent("$useragent");
	$ua->env_proxy;

	my $request   = new HTTP::Request(GET,$url);
	my $response  = $ua->request($request);
	my $xmlresult = $response->content();
  $xmlresult =~ s/<!DOCTYPE.*//;
	my $xp        = XML::XPath->new(xml=>$xmlresult);
	my $nodeset   = $xp->find('//PubmedArticle');

	my %record    = ();

	foreach my $node ($nodeset->get_nodelist) {

		$record{SRC}      = "PubMed";
		$record{journal}  = $node->findvalue('//MedlineJournalInfo/MedlineTA');
		$record{issn}     = $node->findvalue('//Article/Journal/ISSN');
		$record{issn}     = $node->findvalue('//MedlineJournalInfo/ISSNLinking');
		$record{country}  = $node->findvalue('//MedlineJournalInfo/Country');
		$record{NlmJourID}=	$node->findvalue('//MedlineJournalInfo/NlmUniqueID');
		$record{abbrev}   = $node->findvalue('//Article/Journal/ISOAbbreviation');
		
		$record{vol}      = $node->findvalue('//Article/Journal/JournalIssue/Volume');
		$record{issue}    = $node->findvalue('//Article/Journal/JournalIssue/Issue');
		$record{year}     = $node->findvalue('//Article/Journal/JournalIssue/PubDate/Year');
		$record{month}    = $node->findvalue('//Article/Journal/JournalIssue/PubDate/Month');
		$record{day}      = $node->findvalue('//Article/Journal/JournalIssue/PubDate/Day');
		$record{page}     = $node->findvalue('//Article/Pagination/MedlinePgn');

		$record{title}    = $node->findvalue('//Article/ArticleTitle');
		$record{abstract} = $node->findvalue('//Article/Abstract/AbstractText');

		$record{aff}      = $node->findvalue('//Article/Affiliation');
		$record{lang}     = $node->findvalue('//Article/Language');

		$record{AU} = "";
		for (my $i=1; $i <= eval($node->find('count(//Article/AuthorList/Author)')); $i++) {
			$record{surnames}[$i-1]   = $node->findvalue("//Article/AuthorList/Author[$i]/LastName");
			$record{givennames}[$i-1] = $node->findvalue("//Article/AuthorList/Author[$i]/ForeName");
			$record{initials}[$i-1]   = $node->findvalue("//Article/AuthorList/Author[$i]/Initials");
			$record{AU} .= $record{surnames}[$i-1] . ", " . $record{givennames}[$i-1] . "; ";
		}

		my $meshnodes = $node->find('//MeshHeadingList/MeshHeading');
		foreach my $mesh ($meshnodes->get_nodelist) {
			 $descriptor = $mesh->findvalue('DescriptorName');
			 my $qualnodes = $mesh->find('QualifierName');
			 my $i = 0;
			 foreach my $qual ($qualnodes->get_nodelist) {
				  $qualifier = $qual->findvalue('.');
				  push @{$record{MeSH}}, "$descriptor: $qualifier";
					$i++;
			 }
			 if ($i == 0) {
				  push @{$record{MeSH}}, "$descriptor";
			 }
		}
		for (my $i=1; $i <= eval($node->find('count(//ChemicalList/Chemical)')); $i++) {
			$record{Chemicals}[$i-1] = $node->findvalue("//ChemicalList/Chemical[$i]/NameOfSubstance");
			$record{CAS}[$i-1]       = $node->findvalue("//ChemicalList/Chemical[$i]/RegistryNumber");
	  }

		$record{pmid}     = $node->findvalue("//ArticleIdList/ArticleId[\@IdType='pubmed']");
		$record{pmc}      = $node->findvalue("//ArticleIdList/ArticleId[\@IdType='pmc']");
		$record{doi}      = $node->findvalue("//ArticleIdList/ArticleId[\@IdType='doi']");
		#$record{so}       = "$record{journal}. $record{year} $record{month};"
		#						. "$record{vol} ($record{iss}):$record{page}";

	  $record{so} = "";
		$record{so} .= $record{journal} . ". " if (defined($record{journal}));
		$record{so} .= $record{year} if (defined($record{year}));
		$record{so} .= $record{month} if (defined($record{month})) . ";";
		$record{so} .= " " . $record{vol} if (defined($record{vol}));
		$record{so} .= "(" . $record{iss} . ")" if (defined($record{iss}));
		$record{so} .= ":" .$record{page} if (defined($record{page}));

	}
	return(%record);
	#print "$xmlresult";
}

sub pmed2MEDLINE (%) {
# http://www.ncbi.nlm.nih.gov/bookshelf/br.fcgi?book=helppubmed&part=pubmedhelp&rendertype=table&id=pubmedhelp.T44
	my (%record) = @_;
	my $RISstr   = "";

	# $RISstr .= "TA  - $record{journal}\n";
	# $RISstr .= "JF  - $record{journal}\n";
	# $RISstr .= "IS  - $record{issue}\n";
	# $RISstr .= "VL  - $record{vol}\n";
	# my ($startpage, $endpage) = split(/-/, $record{page});
	# $RISstr .= "SP  - $startpage\n";
	# $RISstr .= "EP  - $endpage\n";
	# $RISstr .= "SN  - $record{issn}\n";
	$RISstr .= "PMID- $record{pmid}\n";
	$RISstr .= "IS  - $record{issn}\n";
	$RISstr .= "JT  - $record{journal}\n";
	$RISstr .= "TA  - $record{abbrev}\n";
	$RISstr .= "VI  - $record{vol}\n";
	$RISstr .= "IP  - $record{issue}\n";
	$RISstr .= "DP  - $record{year} $record{month} $record{day}\n";
	$RISstr .= "PY  - $record{year}/$record{month}/$record{day}\n";
	$RISstr .= "PG  - $record{page}\n";
	$RISstr .= "IS  - $record{issn}\n";
	$RISstr .= "AD  - $record{aff}\n";
	$RISstr .= "TI  - $record{title}\n";
	$RISstr .= "AB  - $record{abstract}\n";
	$RISstr .= "LA  - $record{lang}\n";
	$RISstr .= "AID - $record{doi} [doi]\n";
	$RISstr .= 'L1  - http://www.pubmedcentral.nih.gov/articlerender.fcgi?artid='
	        . $record{pmc} . '&blobtype=pdf\n';
	$RISstr .= "M3  - http://dx.doi.org/$record{doi}\n";
	$RISstr .= "PMC - $record{pmc}\n";
	$RISstr .= "SO  - $record{so}\n";
	for (my $i = 0; $i < $#{$record{surnames}}; $i++) {
		$RISstr .= "FAU - " . $record{surnames}[$i] . ", " . $record{givennames}[$i] . "\n";
		$RISstr .= "AU  - "  . $record{surnames}[$i] . ", " . $record{initials}[$i] . "\n";
	}
	for (my $i = 0; $i < $#{$record{MeSH}}; $i++) {
		# $RISstr .= "KW  - " . $record{MeSH}[$i] . "\n";
		$RISstr .= "MH  - " . $record{MeSH}[$i] . "\n";
	}
	for (my $i = 0; $i < $#{$record{Chemicals}}; $i++) {
		$RISstr .= "RN  - " . $record{CAS}[$i] . " (" . $record{Chemicals}[$i] . ")\n";
	}
	# print $RISstr;
	return($RISstr);
}

sub pmed2ISI ($%) {
# http://www.ncbi.nlm.nih.gov/bookshelf/br.fcgi?book=helppubmed&part=pubmedhelp&rendertype=table&id=pubmedhelp.T44
	my ($file, %record) = @_;
	my $RISstr   = "";

	# $RISstr .= "TA  - $record{journal}\n";
	# $RISstr .= "JF  - $record{journal}\n";
	# $RISstr .= "IS  - $record{issue}\n";
	# $RISstr .= "VL  - $record{vol}\n";
	# my ($startpage, $endpage) = split(/-/, $record{page});
	# $RISstr .= "SP  - $startpage\n";
	# $RISstr .= "EP  - $endpage\n";
	# $RISstr .= "SN  - $record{issn}\n";
	$RISstr .= "%J $record{journal}\n";
	$RISstr .= "%V $record{vol}\n";
	$RISstr .= "%N $record{issue}\n";
	$RISstr .= "%D $record{year}\n";
	$RISstr .= "%P $record{page}\n";
	$RISstr .= "%@ $record{issn}\n";
	$RISstr .= "%+ $record{aff}\n";
	$RISstr .= "%T $record{title}\n";
	$RISstr .= "%X $record{abstract}\n";
	$RISstr .= "%G $record{lang}\n";
	$RISstr .= '%U http://www.pubmedcentral.nih.gov/articlerender.fcgi?artid='
	        . $record{pmc} . '&blobtype=pdf\n';
	$RISstr .= "%http://www.ncbi.nlm.nih.gov/sites/entrez/$record{pmid}\n";
	$RISstr .= "%http://dx.doi.org/$record{doi}\n";
	for (my $i = 0; $i < $#{$record{surnames}}; $i++) {
		$RISstr .= "%A " . $record{surnames}[$i] . ", " . $record{givennames}[$i] . "\n";
	}
	$RISstr .= "%K " . $record{MeSH}[0] . "\n";
	for (my $i = 1; $i < $#{$record{MeSH}}; $i++) {
		# $RISstr .= "KW  - " . $record{MeSH}[$i] . "\n";
		$RISstr .= "%" . $record{MeSH}[$i] . "\n";
	}
	for (my $i = 0; $i < $#{$record{Chemicals}}; $i++) {
		$RISstr .= "%" . $record{CAS}[$i] . " (" . $record{Chemicals}[$i] . ")\n";
	}
	# print $RISstr;
	return($RISstr);
}

sub pmed2BibTeX($%) {
	my ($file, %record) = @_;
	my $RISstr   = "";

	# $RISstr .= "TA  - $record{journal}\n";
	# $RISstr .= "JF  - $record{journal}\n";
	# $RISstr .= "IS  - $record{issue}\n";
	# $RISstr .= "VL  - $record{vol}\n";
	# $RISstr .= "SP  - $startpage\n";
	# $RISstr .= "EP  - $endpage\n";
	# $RISstr .= "SN  - $record{issn}\n";
	my ($startpage, $endpage) = split(/-/, $record{page});
	$RISstr .= "author      = \{";
	for (my $i = 0; $i < $#{$record{surnames}}; $i++) {
		$RISstr .= $record{surnames}[$i] . ", " . $record{givennames}[$i] . " AND ";
	}
	$RISstr =~ s/ AND $//;
	$RISstr .= "\},\n";
	$RISstr .= "title       = \{$record{title}\},\n";
	$RISstr .= "journal     = \{$record{journal}\},\n";
	$RISstr .= "volume      = \{$record{vol}\},\n";
	$RISstr .= "number      = \{$record{issue}\},\n";
	$RISstr .= "year        = \{$record{year}\},\n";
	$RISstr .= "pages       = \{$startpage--$endpage\},\n";
	$RISstr .= "issn        = \{$record{issn}\},\n";
	$RISstr .= "jabbrev     = \{$record{abbrev}\},\n";
	$RISstr .= "month       = \{$record{month}\},\n";
	$RISstr .= "day         = \{$record{day}\},\n";
	$RISstr .= "institution = \{$record{aff}\},\n";
	$RISstr .= "abstract    = \{$record{abstract}\},\n";
	$RISstr .= "language    = \{$record{lang}\},\n";
	$RISstr .= "doi         = \{$record{doi}\},\n";
	$RISstr .= "pmid        = \{$record{pmid}\},\n";
	$RISstr .= "pmc         = \{$record{pmc}\},\n";
	$RISstr .= "datasource  = \{NCBI PubMed\},\n";
	$RISstr .= "keywords = \{";
	for (my $i = 0; $i < $#{$record{MeSH}}; $i++) {
		$RISstr .= $record{MeSH}[$i] . " / ";
	}
	for (my $i = 0; $i < $#{$record{Chemicals}}; $i++) {
		$RISstr .= $record{CAS}[$i] . " (" . $record{Chemicals}[$i] . ") / ";
	}
	$RISstr .= "\},\n";
	$RISstr .= "file = \{";
	$RISstr .= "Local:$file:PDF;";
	$RISstr .= "Pubmed:http\\://www.ncbi.nlm.nih.gov/sites/entrez/$record{pmid}:URL;";
	$RISstr .= 'PMC Fulltext:http\://www.pubmedcentral.nih.gov/articlerender.fcgi?artid='
	        . $record{pmc} . '&blobtype=pdf:URL;' if $record{pmc} ne "";

	# $RISstr .= "\},\n";
	# print $RISstr;
	$RISstr =~ s/&lt;/</g;
	$RISstr =~ s/&gt;/>/g;
	return($RISstr);
}
1;

__END__

