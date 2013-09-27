package CGIHelper;
#=========================================================================
#
#    CGIHelper.pm
#
#    Helpers for CGI mainly for JSON/Marc dataset output
#
#    $Id: $
#    Last change: <Fr, 2013/04/12 11:24:40 cdsware zb0035.zb.kfa-juelich.de>
#    Author     : Alexander Wagner
#    Language   : Perl
#
#-------------------------------------------------------------------------
#
#    Copyright (C) 2011 hy Alexander Wagner
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
use utf8;
use locale;
use Encode;
use Sys::Hostname;

use HGF::Forms::HGF;
use HGF::Forms::MarcXML;

my $format = "Marc";

my $useragent          = "Mozilla/5.0 (X11; U; Linux amd64; rv:5.0) Gecko/20100101 Firefox/5.0 (Debian)";
#--------------------------------------------------
# Invenio Connection
my $inveniohost= hostname;
my $invenio    = "http://$inveniohost/search?action_search=Suchen";
my $journalmaster = "http://juser.fz-juelich.de/search?action_search=Suchen";
my $zdbcoll    = "cc=Periodicals";
my $issnsearch = "f=";
my $ofzdb      = "of=zzzdb";
my $ofvdb      = "of=zzvdb";
my $term       = "p=";
my $noofitems  = "rg=25"; # limitation in invenio: not more than 200 at once

#my $issnquery = "$invenio&$zdbcoll&$issnsearch&$ofzdb&$term$issn&$noofitems";

# Link to Pubmed Central
my $pmcprefix  = "http://www.ncbi.nlm.nih.gov/pmc/articles";

#======================================================================

=head1 NAME

=cut
sub SetFormat($) {
	my ($f) = @_;
	$format = $f;
}
sub SetWWWHost($) {
	my ($f) = @_;
	$inveniohost = $f;
  $invenio     = "http://$inveniohost/search?action_search=Suchen";
}
#----------------------------------------------------------------------
=head2 2Marc

Routines for record output to Marc

Status: checked

=cut
#----------------------------------------------------------------------
#----------------------------------------------------------------------
=head3 Dta2Marc

Format a Hash, tagged by subfield codes as Marc21 XML structure

Status: checked

=cut
#----------------------------------------------------------------------

sub Dta2Marc($$$%) {
	my ($tag, $ind1, $ind2, %subfields) = @_;
	my $marc = "";
	$marc = MarcXML::MarcField($tag, $ind1, $ind2, %subfields);
	return($marc);
}

#----------------------------------------------------------------------
=head3 DtaR2Marc

Format an Array of Hashes (tagged by subfield codes) as a repeated
field in Marc21 XML

Status: checked

=cut
#----------------------------------------------------------------------
sub DtaR2Marc($$$@) {
	my ($tag, $ind1, $ind2, @fields) = @_;
	# @fields is an array of hashes. Each hash is keyed by the subfields
	# it contains.
	my $marc = "";
	if ($#fields >= 0) {
		for (my $i = 0; $i <= $#fields; $i++) {
			$marc .= MarcXML::MarcField($tag, $ind1, $ind2, %{$fields[$i]})
		}
	}
	return($marc);
}

#----------------------------------------------------------------------
=head2 2JSON

Routines for record output to JSON

Status: checked

=cut
#----------------------------------------------------------------------
#----------------------------------------------------------------------
=head3 Dta2JSON

Format a Hash, tagged by subfield codes to JSON

Status: checked

=cut
#----------------------------------------------------------------------
sub Dta2JSON($$$%) {
	my ($tag, $ind1, $ind2, %subfields) = @_;
	my $json = "";
	for my $subfield ( sort keys %subfields) {
		if ($subfields{$subfield} ne "") {
			my $s = $subfields{$subfield};
      $s =~ s/\n\r?/ /g;
      $s =~ s/"/'/g;
      $s =~ s/\\/\\\\/g;
			$json .= "  \"I$tag$ind1$ind2$subfield\" : \"$s\",\n";
		}
	}
	return($json);
}

#----------------------------------------------------------------------
=head3 DtaR2JSON

Format an Array of Hashes (tagged by subfield codes) as a repeated
field in Marc21 XML

Status: checked

=cut
#----------------------------------------------------------------------

sub DtaR2JSON($$$@) {
	my ($tag, $ind1, $ind2, @fields) = @_;
	# @fields is an array of hashes. Each hash is keyed by the subfields
	# it contains.
	my $json = "";

	if ($#fields >= 0) {
		$json .= "  \"I$tag$ind1$ind2\" : \"[";
		for (my $i = 0; $i <= $#fields; $i++) {
			$json .= " {";
			for my $k (sort keys %{$fields[$i]}) {
				my $f = $fields[$i]{$k};
				$f =~ s/\n/ /g;
				$f =~ s/"/'/g;
        $f =~ s/\\/\\\\/g;
				$json .= "\\\"$k\\\" : \\\"$f\\\", ";
			}
			$json .= "}, ";
		}
		$json .= "]\",\n";
	}
	return($json);
}

#----------------------------------------------------------------------
=head2 2Output

Generic routines for record output that switch the format defined

Status: checked

=cut
#----------------------------------------------------------------------
#----------------------------------------------------------------------
=head3 Dta2Output

Format a Hash, tagged by subfield codes as Marc21 XML or JSON
structure, depending on the global output $format

Status: checked

=cut
#----------------------------------------------------------------------
sub Dta2Output($$$%) {
	my ($tag, $ind1, $ind2, %subfields) = @_;
	if ($format ne "Marc") {
		 $ind1 = "_" if ($ind1 eq " ");
		 $ind2 = "_" if ($ind2 eq " ");
	}
	my $output = "";
	# By default generate JSON
	if ($format eq "Marc") {
		$output = Dta2Marc($tag, $ind1, $ind2, %subfields);
	} else {
		# In JSON: push all authors to the 100 field, ie. one single
		# field. This is not correct in Marc-speak but our web forms only
		# know "Author" as one single field.
		$tag = "100" if ($tag eq "700");
		$output = Dta2JSON($tag, $ind1, $ind2, %subfields);
	}
	return($output);
}

#----------------------------------------------------------------------
=head3 DtaR2Marc

Format an Array of Hashes (tagged by subfield codes) as a repeated
field in Marc21 XML or a proper JSON, depending on global $format

Status: checked

=cut
#----------------------------------------------------------------------
sub DtaR2Output($$$@) {
	my ($tag, $ind1, $ind2, @fields) = @_;
	# @fields is an array of hashes. Each hash is keyed by the subfields
	# it contains.
	if ($format ne "Marc") {
		 $ind1 = "_" if ($ind1 eq " ");
		 $ind2 = "_" if ($ind2 eq " ");
	}
	my $output = "";
	if ($format eq "Marc") {
		$output = DtaR2Marc($tag, $ind1, $ind2, @fields);
	} else {
		$tag = "100" if ($tag eq "700");
		$output = DtaR2JSON($tag, $ind1, $ind2, @fields);
	}
	return($output);
}

sub ParseZZZDB($) {
	my ($line) = @_;
	my %jrecord = ();
	$line =~ s/\n//;
        ($inveniojournalid, 
                 $jrecord{zdbid},
                 $jrecord{journal},
                 $jrecord{issnlst},
                 $jrecord{idlist},
                 $jrecord{statkeys},
                 $jrecord{ddc},
                 $jrecord{place},
                 $jrecord{publisher},
    	) = split(/\|/, $line);
      $jrecord{SRC} = "$inveniohost";
      my (@issns) = split(/ /, $jrecord{issnlst});
      $jrecord{issn} = $issns[0];
	return(%jrecord)
}

#----------------------------------------------------------------------
# All databases should have given back their records, no ISSN passed in the
# call try to extract it from those records. Start with records of worst
# quality and work up the row to get the most trustable value.
sub FetchISSN($) {
	my ($issn) = @_;
	my %jrecord = ();
	#----------------------------------------------------------------------
	if (defined($issn) and ($issn ne "")) {
		# An ISSN was passed on or retrieved via previous steps. Call up Invenio
		# to link the ISSN to the ZDB-ID of the journal, get proper journal
		# naming and DB coverage from Invenio

		# Build up a query against Invenio to fetch the ZDBID
		my $query = "$invenio&$zdbcoll&$issnsearch&$ofzdb&$term$issn";
		my $ua = new LWP::UserAgent;
		$ua->agent("$useragent");
		$ua->env_proxy;
		my $request   = new HTTP::Request("GET",$query);
		my $response  = $ua->request($request);
		my $line      = $response->content();
if ($line eq '') {
       # we got no response: we do not have the jouranl in question.
       # Try to ask $journalmaster as it might already have the
       # journal in question. This is more expensive as in principle
       # it goes over the network.
       my $query = "$journalmaster&$zdbcoll&$issnsearch&$ofzdb&$term$issn";
       my $request   = new HTTP::Request("GET",$query);
       my $response  = $ua->request($request);
       $line      = $response->content();
}
		%jrecord = ParseZZZDB($line);
		$jrecord{SRC} = "$inveniohost";
		$jrecord{issn} = $issn;
	}
	return(%jrecord);
}

sub FetchByName($) {
	my ($name) = @_;
	my %jrecord = ();
	#----------------------------------------------------------------------
	if (defined($name) and ($name ne "")) {
		# we got only a name. Search in in 0247_a only and as exact string 
                # as this is the only way to hope for a unique match.
                # This is meant mainly for WoS lookups via LITE interface where we get 
                # only the strange (but unique) WoS-Journalname.

		# Build up a query against Invenio to fetch the ZDBID
		my $query = "$invenio&$zdbcoll&$issnsearch&$ofzdb&$term" . "0247_a:" . "\"$name\"";
		my $ua = new LWP::UserAgent;
		$ua->agent("$useragent");
		$ua->env_proxy;
		my $request   = new HTTP::Request("GET",$query);
		my $response  = $ua->request($request);
		my $line      = $response->content();
		%jrecord = ParseZZZDB($line);
		$jrecord{SRC} = "$inveniohost";
	}
	return(%jrecord);
}

sub CheckID4Dupes(@) {
  my %matches = ();
  foreach my $id (@_) {
    my $query = "$invenio&$ofvdb&$term" . '0247_a:"' . $id . '"';
    my $ua = new LWP::UserAgent;
    $ua->agent("$useragent");
    $ua->env_proxy;
    my $request   = new HTTP::Request("GET",$query);
    my $response  = $ua->request($request);
    my $contents = $response->content();
    my @lines = split(/\n/, $contents);
    foreach $line (@lines) {
      my $recid = $line;
      $recid =~ s/\|.*$//;
      $matches{$recid}++;
    }
  }
  return %matches;
}

#----------------------------------------------------------------------
sub CopyWoS($%) {
	my ($mode, %wosrec) = @_;
	my %record = ();
	if ((defined($wosrec{RecCount})) and ($wosrec{RecCount} == 1)) {
		$record{SRC}      = $wosrec{"0-SRC"} . ", ";
		$record{ut}       = $wosrec{"0-UT"};
		$record{ck}       = $wosrec{"0-CK"};
		$record{extent}   = $wosrec{"0-PG"};
		$record{lang}     = $wosrec{"0-LA"};
		$record{title}    = $wosrec{"0-TI"};
		$record{wostype}  = $wosrec{"0-PT"};
		# C1
		$record{C1}       = $wosrec{"0-C1"};
		# Journal should always match against Invenio, do not set it here
		$record{volume}   = $wosrec{"0-VL"};
		$record{issue}    = $wosrec{"0-IS"};
		$record{year}     = $wosrec{"0-PY"};
		$record{bpage}    = $wosrec{"0-BP"};
		$record{epage}    = $wosrec{"0-EP"};
 	 	$record{comment} .= $wosrec{"0-FundAckTxt"} if (defined($wosrec{"0-FundAckTxt"}));

		# WoS Author tags: improve this via the fields
		# AuthorLastName, AuthorFirstName and add addresses
		$record{AU}       = $wosrec{"0-AU"};
		$record{AF}       = $wosrec{"0-AF"};

		# Split the simple field first as we always have this
		my @authors = split(/; /, $wosrec{"0-AU"});
		my $i = 0;
		foreach my $a (@authors) {
			$record{"$i-au"} .= $a;
			$i++;
		}
		# Now try if we can get better information
		$i = 0;
		foreach my $a (@{$wosrec{"0-AuthorLastName"}}) {
			$record{"$i-au"}  = $wosrec{"0-AuthorLastName"}[$i] . ", ";
			$record{"$i-au"} .= $wosrec{"0-AuthorFirstName"}[$i];
			$i++;
		}

		$record{EM}       = $wosrec{"0-EM"};
		# TODO add author addresses

		# WoS indexing and abstract
		if ($mode ne "thin") {
			$record{abstract} = $wosrec{"0-AB"};
			$record{SC}       = $wosrec{"0-SC"}; # subject categories
			$record{DE}       = $wosrec{"0-DE"}; # keywords
			$record{ID}       = $wosrec{"0-ID"}; # keywords Plus
		}

    $i = 0;
		foreach my $a (@{$wosrec{'0-FundingAgency'}}) {
			push @{$record{FundingAgency}}, $a;
      my $g = $wosrec{'0-GrantNo'}[$i];
		  push @{$record{GrantNo}}, $g;
      $i++;
		}
	}
	return(%record);
}

sub CopyInspire ($%) {
	my ($mode, %inspirerec) = @_;
	my %record = ();
	if (defined($inspirerec{INSPIRE})) {
		$SRC .= $inspirerec{"SRC"} . ", ";
		$record{doi}       = $inspirerec{doi}   if (defined($inspirerec{doi}  ) and ($inspirerec{doi}   ne ""));
		$record{title}     = $inspirerec{title} if (defined($inspirerec{title}) and ($inspirerec{title} ne ""));
		$record{abstract}  = $inspirerec{abstract} if (defined($inspirerec{abstract}) and ($inspirerec{abstract} ne ""));
		$record{volume}    = $inspirerec{vol}   if (defined($inspirerec{vol}  ) and ($inspirerec{vol}   ne ""));
		$record{issue}     = $inspirerec{issue} if (defined($inspirerec{issue}) and ($inspirerec{issue} ne ""));
		$record{year}      = $inspirerec{year}  if (defined($inspirerec{year} ) and ($inspirerec{year}  ne ""));
		$record{page}      = $inspirerec{page}  if (defined($inspirerec{page} ) and ($inspirerec{page}  ne ""));
		$record{repno}     = $inspirerec{repno} if (defined($inspirerec{repno}) and ($inspirerec{repno} ne ""));
		my $i=0;
		foreach my $au (split(";",$inspirerec{AU})) {
			$record{"$i-au"}  = $au;
			$i++;
		}

		if ($mode ne "thin") {
			 $record{abstract}  = $inspirerec{abstract};
		}
	  $record{comment}  = $inspirerec{comments} if (defined($inspirerec{comments}) and ($inspirerec{comments} ne ""));
	}
	return(%record);
}


sub CopyarXiv($%) {
	my ($mode, %arxivrec) = @_;
	my %record = ();
	if (defined($arxivrec{arXiv})) {
		$SRC .= $arxivrec{"SRC"} . ", ";
		$record{doi}       = $arxivrec{doi}   if (defined($arxivrec{doi}  ) and ($arxivrec{doi}   ne ""));
		$record{title}     = $arxivrec{title} if (defined($arxivrec{title}) and ($arxivrec{title} ne ""));
		$record{arXiv}     = $arxivrec{arXiv} if (defined($arxivrec{arXiv}) and ($arxivrec{arXiv} ne ""));
		$record{volume}    = $arxivrec{vol}   if (defined($arxivrec{vol}  ) and ($arxivrec{vol}   ne ""));
		$record{issue}     = $arxivrec{issue} if (defined($arxivrec{issue}) and ($arxivrec{issue} ne ""));
		$record{year}      = $arxivrec{year}  if (defined($arxivrec{year} ) and ($arxivrec{year}  ne ""));
		$record{page}      = $arxivrec{page}  if (defined($arxivrec{page} ) and ($arxivrec{page}  ne ""));
		$record{repno}     = $arxivrec{repno} if (defined($arxivrec{repno}) and ($arxivrec{repno} ne ""));
    my $i=0;
		foreach my $au (@{$arxivrec{surnames}}) {
			$record{"$i-au"}  = $arxivrec{surnames}[$i] . ", ";
			$record{"$i-au"} .= $arxivrec{givennames}[$i];
			$i++;
		}

		if ($mode ne "thin") {
			 $record{abstract}  = $arxivrec{abstract};
		}
	  $record{comment}  = $arxivrec{comments};
	}
	return(%record);
}

sub CopyInspec($%) {
	my ($mode, %inhrec) = @_;
	my %record = ();
	if (defined($inhrec{"0-UT"})) {
		$record{SRC}       = $inhrec{"0-SRC"} . ", ";
		$record{inspecid}  = $inhrec{"0-UT"}    if defined($inhrec{"0-UT"});
		$record{title}     = $inhrec{"0-TI"}    if defined($inhrec{"0-TI"});
		$record{lang}      = $inhrec{"0-LA"}    if defined($inhrec{"0-LA"});
		$record{inhtype}   = $inhrec{"0-DT"}    if defined($inhrec{"0-DT"});
		$record{volume}    = $inhrec{"0-VL"}    if defined($inhrec{"0-VL"});
		$record{issue}     = $inhrec{"0-IS"}    if defined($inhrec{"0-IS"});
		$record{year}      = $inhrec{"0-PY"}    if defined($inhrec{"0-PY"});
		$record{bpage}     = $inhrec{"0-BP"}    if defined($inhrec{"0-BP"});
		$record{epage}     = $inhrec{"0-EP"}    if defined($inhrec{"0-EP"});
		$record{booktitle} = $inhrec{"0-btl"}   if defined($inhrec{"0-btl"});
		$record{publisher} = $inhrec{"0-pub"}   if defined($inhrec{"0-pub"});
		$record{place}     = $inhrec{"0-place"} if defined($inhrec{"0-place"});
		$record{isbn}      = $inhrec{"0-ISBN"}  if defined($inhrec{"0-ISBN"});

		if ($mode ne "thin") {
			 # INH Indexing:
			 $record{abstract}  = $inhrec{"0-AB"}    if defined($inhrec{"0-AB"});
			 my $value = $inhrec{"0-ID"};
			 my @headings = split(/\t/, $value);
			 my %uniqueheadings = ();
			 foreach my $h (@headings) {
				 $uniqueheadings{$h}++;
			 }
			 for my $key (sort(keys %uniqueheadings)) {
				 push @{$record{InspecKW}}, $key;
			 }

			 %uniqueheadings = ();
			 $value = $inhrec{"0-SC"};
			 @headings = split(/\t/, $value);
			 foreach my $h (@headings) {
				 $uniqueheadings{$h}++;
			 }
			 for my $key (sort( keys %uniqueheadings)) {
				 push @{$record{InspecSC}}, $key;
			 }
		}
	}
	return(%record);
}

sub CopyPubmed($%) {
	my ($mode, %pmrec) = @_;
	my %record = ();
	if (defined($pmrec{pmid})) {
		$record{SRC}       = $pmrec{SRC} . ", ";
		$record{title}     = $pmrec{title};
		$record{lang}      = $pmrec{lang};
		$record{pmid}      = $pmrec{pmid};
		$record{pmc}       = $pmrec{pmc} if ($pmrec{pmc} ne "");
		my $i = 0;
		foreach my $au (@{$pmrec{surnames}}) {
			$record{"$i-au"}  = $pmrec{surnames}[$i] . ", ";
			$record{"$i-au"} .= $pmrec{givennames}[$i];
			$i++;
		}
		$record{volume}    = $pmrec{vol};
		$record{issue}     = $pmrec{issue};
		$record{year}      = $pmrec{year};
		$record{page}      = $pmrec{page};

		if ($mode ne "thin") {
			 $record{abstract}  = $pmrec{abstract};
			 # The following assign arrays
			 $record{MeSH}      = $pmrec{MeSH};
			 $record{Chemicals} = $pmrec{Chemicals};
			 $record{CAS}       = $pmrec{CAS};
		}
	}
	return(%record);
}

sub CopyGVK($%) {
	my ($mode, %bookrec) = @_;
	my %record = ();
	if (defined($bookrec{ppn})) {
		$record{SRC}             = $bookrec{"SRC"} . ", ";
		$record{ppn}             = $bookrec{ppn};
		$record{title}           = $bookrec{title};
		$record{firstauthor}     = $bookrec{firstauthor};
		$record{"0-au"}          = $bookrec{"0-au"};
		$record{"1-au"}          = $bookrec{"1-au"};
		$record{"2-au"}          = $bookrec{"2-au"};
		$record{"0-book-editor"} = $bookrec{"0-editor"};
		$record{"1-book-editor"} = $bookrec{"1-editor"};
		$record{"2-book-editor"} = $bookrec{"2-editor"};
    $record{"other"}         = $bookrec{"other"};
    $record{"other-func"}    = $bookrec{"other-func"};

		$record{lang}            = $bookrec{language};
		$record{bookpublisher}   = $bookrec{bookpublisher};
		$record{bookplace}       = $bookrec{bookplace};
		$record{extent}          = $bookrec{pages};
		$record{bookyear}        = $bookrec{bookyear};
		$record{bookseries}      = $bookrec{series};
		$record{bookvol}         = $bookrec{volume};
		$record{hsv1}            = $bookrec{hsv1};
		$record{hsv2}            = $bookrec{hsv2};
		$record{isbn}            = $bookrec{isbn};
		$record{sisbn}           = $bookrec{sisbn};
		$record{edition}         = $bookrec{edition};
		$record{ddc}             = $bookrec{ddc};
		$record{url}             = $bookrec{url};
		$record{illustration}    = $bookrec{illustration};
		
		if ($mode ne "thin") {
			 $record{loc}             = $bookrec{loc};
			 # The following assign arrays
			 $record{MeSH}            = $bookrec{MeSH};

			 # BNB & LoC should assign identical headings. We do not need both
			 # so unique them before storing
			 my %done = ();
			 my $i = 0;
			 foreach my $k (@{$bookrec{BLLCSH}}) {
				 if (not defined($done{$k})) {
					 $record{LCSH}[$i] = $k;
					 $done{$k} = $k;
					 $i++;
				 }
			 }
			 foreach my $k (@{$bookrec{LCSH}}) {
				 if (not defined($done{$k})) {
					 $record{LCSH}[$i] = $k;
					 $done{$k} = $k;
					 $i++;
				 }
			 }
			 $record{SWD}           = $bookrec{SWD};
			 $record{DDB}           = $bookrec{DDB};
			 $record{RVK}           = $bookrec{RVK};
			 $record{comment}       = $bookrec{comment};
		}
	}
	return(%record);
}

#----------------------------------------------------------------------
sub ConstructRecord($%%%%%%%%) {
# All possible data is retrieved, now build up the final record

	my ($mode)   = $_[0];
	# Pass all hashes as references to sort them in correctly
	my %cxrec    = %{$_[1]};
	my %inhrec   = %{$_[2]};
	my %pmrec    = %{$_[3]};
	my %arxivrec = %{$_[4]};
	my %wosrec   = %{$_[5]};
	my %bookrec  = %{$_[6]};
	my %jrecord  = %{$_[7]};
	my %inspirerec = %{$_[8]};

	my %record = ();
	my $SRC    = "";  # Data sources used

	#---------- Web of Science
	%rec = ();
	%rec = CopyWoS($mode, %wosrec);
	for my $k (keys (%rec)) {
		$record{$k} = $rec{$k};
	}
	$SRC .= $rec{SRC} . ", " if (defined($rec{SRC}));

	#---------- arXiv
	%rec = ();
	%rec = CopyarXiv($mode, %arxivrec);
	for my $k (keys (%rec)) {
		$record{$k} = $rec{$k};
	}
	$SRC .= $rec{SRC} . ", " if (defined($rec{SRC}));

	#---------- CrossRef
	for my $k (sort keys(%cxrec)) {
			next if $k eq "SRC";
			$record{$k} = $cxrec{$k};
	}
	$SRC .= $cxrec{SRC} . ", " if (defined($cxrec{SRC}));

	#---------- Journal data
	for my $k (sort keys(%jrecord)) {
			next if $k eq "SRC";
			$record{$k} = $jrecord{$k};
	}
	$SRC .= $jrecord{SRC} . ", " if (defined($jrecord{SRC}));

	#---------- Inspec
	%rec = ();
	%rec = CopyInspec($mode, %inhrec);
	for my $k (keys (%rec)) {
		$record{$k} = $rec{$k};
	}
	$SRC .= $rec{SRC} . ", " if (defined($rec{SRC}));

	#---------- Pubmed
	%rec = ();
	%rec = CopyPubmed($mode, %pmrec);
	for my $k (keys (%rec)) {
		$record{$k} = $rec{$k};
	}
	$SRC .= $rec{SRC} . ", " if (defined($rec{SRC}));

	#---------- GVK union catalogue
	%rec = ();
	%rec = CopyGVK($mode, %bookrec);
	for my $k (keys (%rec)) {
		$record{$k} = $rec{$k};
	}
	$SRC .= $rec{SRC} . ", " if (defined($rec{SRC}));
	
	if (not defined($record{pages})) {
		 $record{pages}  = $record{bpage} . " - " if (defined($record{bpage}));
		 $record{pages} .= $record{epage}         if (defined($record{epage}));
	}
	$SRC =~ s/, $//;
	$record{SRC} = $SRC;

	#---------- INSPIRE
	%rec = ();
	%rec = CopyInspire($mode, %inspirerec);
	for my $k (keys (%rec)) {
		$record{$k} = $rec{$k};
	}
	$SRC .= $rec{SRC} . ", " if (defined($rec{SRC}));


	return(%record)
}

#----------------------------------------------------------------------
sub MakeOutput($$%) {
	my ($format, $mode, %record) = @_;

	SetFormat($format);

	my %confdta  = ();
	my $masterid = "";
  # masterta is an array of hashes
	my $masterta = "";
#	if ($format ne "Marc") {
#		$masterta = "";
#	}

	# ----------------------------------------------------------------------
	# First construct the master records. This applies to works
	# published "within" something or that are "part of" something.
	# 
 	# We have a book, so the master has to be a book
  my $bookmaster  = "";
  my $confmaster  = "";
  my $grantmaster = "";
 	if ($record{SRC} =~ /CrossRef Book/) {
		 my @MRFields = ();
 		 if (defined($record{bookpisbn})) {
			 my %marcdta = ();
 			 $marcdta{"a"} = $record{bookpisbn} . ' (print)';
 			 push (@MRFields, { %marcdta });
 		 }
 		 if (defined($record{bookeisbn})) {
			 my %marcdta = ();
 			 $marcdta{"a"} = $record{bookeisbn} . ' (electronic)';
 			 push (@MRFields, { %marcdta });
 		 }
 		 $bookmaster .= CGIHelper::DtaR2Output("020", " ", " ", @MRFields);

 		 my %marcdta = ();
 		 @MRFields = ();
 		 if (defined($record{bookdoi})) {
			 my %marcdta = ();
 			 $marcdta{"a"} = $record{bookdoi};
 			 $marcdta{"2"} = "doi";
 			 push (@MRFields, { %marcdta });
 		 }
 		 $bookmaster .= CGIHelper::DtaR2Output("024", "7", " ", @MRFields);
 
 		 $masterid  = "Book-";
 		 if (defined($record{bookdoi})) {
 				$masterid .= $record{bookdoi}
 		 } elsif (defined($record{bookeisbn})) {
 				$masterid .= $record{bookeisbn}
 		 } elsif (defined($record{bookpisbn})) {
 				$masterid .= $record{bookpisbn}
 		 } elsif (defined($record{booktitle})) {
 				my $ti = $record{booktitle};
 				$ti =~ s/ //g;
 				$masterid .= substr($ti, 1, 10);
 		 }
 		 $masterid =~ s/ /_/g;
 		 $masterid =~ s/,//g;
 		 %marcdta = ();
 		 $marcdta{a} = $masterid;
 		 $bookmaster .= CGIHelper::Dta2Output("037", " ", " ", %marcdta);

 		 @MRFields = ();
 		 %marcdta  = ();
 		 if (defined($record{bookplace})) {
 			 $marcdta{"b"} = $record{bookplace};
 		 }
 		 if (defined($record{bookpublisher})) {
 			 $marcdta{"a"} = $record{bookpublisher};
 		 }
 		 if (defined($record{bookyear})) {
 			 $marcdta{"c"} = $record{bookyear};
 		 }
		 if (defined($record{publisher})) {
 			 $marcdta{"a"} = $record{publisher};
		 }
		 if (defined($record{place})) {
 			 $marcdta{"b"} = $record{bookplace};
		 }
 		 push (@MRFields, { %marcdta });
 		 $bookmaster .= CGIHelper::DtaR2Output("260", " ", " ", @MRFields);

 		 %marcdta = ();
 		 if (defined($record{booktitle})) {
 			 $marcdta{a} = $record{booktitle};
 		 }
 		 $bookmaster .= CGIHelper::Dta2Output("245", " ", " ", %marcdta);
 		 my $i = 0;

 		 @MRFields = ();
 		 while (defined($record{"$i-book-editor"})) {
			 my %marcdta = ();
 			 $marcdta{"a"} = $record{"$i-au"};
 			 $marcdta{"b"} = $i;
 			 $marcdta{"e"} = "Editor";
 			 $i++;
 			 push (@MRFields, { %marcdta });
 		 }
 		 $bookmaster .= CGIHelper::DtaR2Output("700", "1", " ", @MRFields);

 		 @MRFields = ();
		 $marcdta{a} = "book";
 		 push(@MRFields, {%marcdta});
		 $marcdta{a} = "autogen";
 		 push(@MRFields, {%marcdta});
 		 $bookmaster .= CGIHelper::DtaR2Output("980", " ", " ", @MRFields);
 
     # Check if we have this key already. However, as this is no sharp
     # key, it's up to the library to handle it properly.
     # TODO enable dupechecking
     ### my %matches = CheckID4Dupes($masterid);
     ### if (keys(%matches) > 0) {
     ###    $bookmaster = "";
     ### }
 	}
	# Master record for a book finished.
	# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
	# ...but we might have a conference to refer to...
	#  
 	elsif ($record{SRC} =~ m/CrossRef Conference/) {
 	# We have a conference, so the master is to be a conference
 		 
 		 $masterid = "Conf-" . $record{confsyear}
 								 . $record{confsmonth} . $record{confsday}  . "_"
 								 . $record{conflocation};
 		 $masterid =~ s/ /_/g;
 		 $masterid =~ s/,//g;
 		 my %marcdta = ();
 		 $marcdta{a} = $masterid;
 		 $confmaster .= CGIHelper::Dta2Output("037", " ", " ", %marcdta);
 		 my $confdate = $record{confsday}    . "-" 
 								  . $record{confsmonth} .  "-"
 									. $record{confsyear}  . " - "
 									. $record{confeday}   . "-"
 									. $record{confemonth} . "-"
 									. $record{confeyear};
 		 my @MRFields = ();
		 %marcdta  = ();
		 %confdta  = ();
 		 $confdta{"a"} = $record{confname};
 		 $confdta{"c"} = $record{conflocation};
 		 $confdta{"d"} = $confdate;
 		 $confdta{"p"} = $record{proctitle};
 		 $confdta{"0"} = $masterid;
 		 push (@MRFields, { %confdta });
 		 $confmaster .= CGIHelper::DtaR2Output("111", "2", " ", @MRFields);
 
 		 @MRFields = ();
		 $marcdta{a} = "event";
 		 push(@MRFields, {%marcdta});
		 $marcdta{a} = "autogen";
 		 push(@MRFields, {%marcdta});
 		 $confmaster .= CGIHelper::DtaR2Output("980", " ", " ", @MRFields);

     # Check if we have this key already. However, as this is no sharp
     # key, it's up to the library to handle it properly.
     # TODO Enable dupechecking
     ### my %matches = CheckID4Dupes($masterid);
     ### if (keys(%matches) > 0) {
     ###    $confmaster = "";
     ### }
	}

  $i = 0;
  foreach $fa (@{$record{"FundingAgency"}}) {
    my @grants = split(/\t/, $record{"GrantNo"}[$i]) if (defined($record{"GrantNo"}[$i]));
    foreach $g (@grants) {
      # CheckID4Dupes builds a usual search query. Therefore, we can
      # append the collection limiter.
      my %matches = CheckID4Dupes($g . '&cc=Grants');
      if (keys(%matches) <= 0) {
         # We do not need to generate a Grant if we have it already.

         ## # 150
         ## %marcdta = ();
         ## $marcdta{"a"} = "G:($fa)$g";
 		     ## $grantmaster .= CGIHelper::Dta2Output("150", " ", " ", %marcdta);

         # 024 7_
         $grantmaster .= "{\n";
         @MRFields = ();
         $marcdta{"a"} = $g;
         $marcdta{"2"} = $fa;
         push (@MRFields, { %marcdta });
         $grantmaster .= CGIHelper::DtaR2Output("024", "7", " ", @MRFields);

         # 035
         %marcdta = ();
         $marcdta{"a"} = "G:($fa)$g";
         $marcdta{"a"} =~ s/ //g;
         $grantmaster .= CGIHelper::Dta2Output("035", " ", " ", %marcdta);

         # 150
         %marcdta = ();
         $marcdta{"a"} = "$fa: $g";
         $grantmaster .= CGIHelper::Dta2Output("150", " ", " ", %marcdta);

         %marcdta = ();
         $marcdta{"a"} = "G";
         $grantmaster .= CGIHelper::Dta2Output("980", " ", " ", %marcdta);

         %marcdta = ();
         $marcdta{"a"} = "AUTHORITY";
         $grantmaster .= CGIHelper::Dta2Output("980", " ", " ", %marcdta);
         %marcdta = ();
         $marcdta{"a"} = "autogen";
         $grantmaster .= CGIHelper::Dta2Output("980", " ", " ", %marcdta);
         $grantmaster .= "\n},";
      }
    }
    $i++;
  }

	#----------------------------------------------------------------------
	# Finish of Master records

	my $dtarec = "";
	if ($format eq "Marc") {
		 $dtarec .= '<?xml version="1.0" ?>' . "\n";
		 $dtarec .= '<collection xmlns="http://www.loc.gov/MARC21/slim">' . "\n";
	}

	if ($format eq "Marc") {
    if ($bookmaster ne "") {
    }
    if ($confmaster ne "") {
    }

  } else {
    # package the master record(s) into an array structure. We end up
    # with n bibliographic entities, each a component of this very
    # array.
    $masterta = "[ ";
    if ($bookmaster ne "") {
      $bookmaster = "{" . $bookmaster . "},";
      $masterta .= $bookmaster;
    }
    if ($confmaster ne "") {
      $confmaster = "{" . $confmaster . "},";
      $masterta .= $confmaster;
    }
    if ($grantmaster ne "") {
      # grantmaster is already some array
      $masterta .= $grantmaster;
    }
    $masterta =~ s/,$//;
    $masterta .= " ]";
  }

	if ($format eq "Marc") {
		 $dtarec .= '<record>' . "\n";
	} else {
		 $dtarec .= "{\n";
	}

  $masterta = "{}" if $masterta =~ m/\[\s{1,}\]/;
  $masterta = "{}" if $masterta eq "";
	if ($masterta ne "{}") {
		if ($format eq "Marc") {
			$dtarec .= $masterta;
		  $dtarec .= '</record>';
		  $dtarec .= "\n\n";
			# We have to open the second record as well.
		  $dtarec .= '<record>';
		  $dtarec .= "\n";
		} else {
			# Escape all " so that jQuery thinks it is just a string
			$masterta =~ s/\\/\\\\/g;
			$masterta =~ s/"/\\"/g;
			$masterta =~ s/\\\\\\"/\&quot;/g;
			#$masterta =~ s/\n//g;
			$dtarec .= '  "Ihgf_master" : "' . $masterta . "\",\n";
		}
	}

	my @MRFields = ();
	my %marcdta  = ();
	if (defined($record{isbn})) {
		my %marcdta = ();
		$marcdta{'a'} = $record{'isbn'};
		push (@MRFields, { %marcdta });
	}
	if (defined($record{sisbn})) {
		my %marcdta = ();
		$marcdta{a} = $record{sisbn};
		push (@MRFields, { %marcdta });
	}

	# We got book-isbns from crossref
	if (defined($record{bookpisbn})) {
		my %marcdta = ();
		$marcdta{a} = $record{bookpisbn} . ' (print)';
		push (@MRFields, { %marcdta });
	}
	if (defined($record{bookeisbn})) {
		my %marcdta = ();
		$marcdta{a} = $record{bookeisbn} . ' (electronic)';
		push (@MRFields, { %marcdta });
	}
  if ($#MRFields > 0) {
	  $dtarec .= CGIHelper::DtaR2Output("020", " ", " ", @MRFields);
  }

 	# Identifier
  my @uniqueIDs = ();
 	@MRFields = ();
 	if (defined($record{ppn})) {
		my %marcdta = ();
 		$marcdta{"2"} = "GVK";
 		$marcdta{"a"} = "GVK:" . $record{ppn};
    push (@uniqueIDs, $marcdta{"a"});
 		push (@MRFields, { %marcdta });
 	}
 	if (defined($record{doi})) {
		my %marcdta = ();
 		$marcdta{"2"} = "doi";
 		$marcdta{"a"} = $record{doi};
    push (@uniqueIDs, $marcdta{"a"});
 		push (@MRFields, { %marcdta });
 	}
 	if (defined($record{ut})) {
		my %marcdta = ();
    $record{ut} =~ s/ISI:/WOS:/;    # WoS changed prefix normalize it
 	 	$marcdta{"2"} = "WOS";
 	 	$marcdta{"a"} = $record{ut};
    push (@uniqueIDs, $marcdta{"a"});
 		push (@MRFields, { %marcdta });
 	}
 	if (defined($record{pmid})) {
		my %marcdta = ();
 	 	$marcdta{"2"} = "pmid";
 	 	$marcdta{"a"} = "pmid:" . $record{pmid};
    push (@uniqueIDs, $marcdta{"a"});
 		push (@MRFields, { %marcdta });
 	}
 	if ((defined($record{pmc})) and ($record{pmc} ne "")){
		my %marcdta = ();
 	 	$marcdta{"2"} = "pmc";
 	 	$marcdta{"a"} = "pmc:" . $record{pmc};
    push (@uniqueIDs, $marcdta{"a"});
 		push (@MRFields, { %marcdta });
 
 	 	# If there is a PMC, there is also a fulltext available
 		%marcdta = ();
 	 	$marcdta{u} = "$pmcprefix/$record{pmc}";
 	 	$marcdta{2} = "Pubmed Central";
 		$dtarec .= CGIHelper::Dta2Output("856", "7", " ", %marcdta);
 	}
 	if (defined($record{inspecid})) {
 	 	# inspecid is prefixed with inh: already
		my %marcdta = ();
 	 	$marcdta{"2"} = "inh";
 	 	$marcdta{"a"} = $record{inspecid};
    push (@uniqueIDs, $marcdta{"a"});
 		push (@MRFields, { %marcdta });
 	}
	if (defined($record{issnlst})) {
	 	# We do not catalogue journals so the ISSN goes to 024
	 	# not to 022
	 	my @issns = split(/ / , $record{issnlst});
	 	if ($#issns > 0) {
	 		 my %marcdta  = ();
	 		 foreach $i (@issns) {
	 			 %marcdta = ();
	 			 $marcdta{"2"} = "ISSN";
	 			 $marcdta{"a"} = $i;
	 			 push (@MRFields, { %marcdta });
	 		 }
	 	}
	}
 	if (defined($record{arXiv})) {
		my %marcdta = ();
 	 	$marcdta{"2"} = "arXiv";
 	 	$marcdta{"a"} = "arXiv:" . $record{arXiv};
    push (@uniqueIDs, $marcdta{"a"});
 		push (@MRFields, { %marcdta });
  }

 	$dtarec .= CGIHelper::DtaR2Output("024", "7", " ", @MRFields);
 
 	if (defined($record{lang})) {
 		my %marcdta = ();
 	 	$marcdta{a} = "$record{lang}";
 		$dtarec .= CGIHelper::Dta2Output("041", " ", " ", %marcdta);
 	}
 
 	if (defined($record{ddc})) {
 		my %marcdta = ();
 	 	$marcdta{a} = "$record{ddc}";
 		$dtarec .= CGIHelper::Dta2Output("082", " ", " ", %marcdta);
 	}
 
	if ($mode ne "thin") {
		 @MRFields = ();
		 foreach my $t (@{$record{InspecSC}}){
			 my %marcdta = ();
			 $marcdta{"2"} = "Inspec";
			 $marcdta{"0"} = $t;
			 push (@MRFields, { %marcdta });
		 }
		 $dtarec .= CGIHelper::DtaR2Output("084", " ", " ", @MRFields);
	}

	%marcdta = ();
	my $austr = "";
 	@MRFields = ();
  my $b = 0;
 	if (defined($record{firstauthor})) {
 		my %marcdta = ();
		$austr .= $record{firstauthor} . " ; ";
 	 	$marcdta{"a"} = $record{firstauthor};
 	 	$marcdta{"b"} = "$b";
    $b++;
 		push (@MRFields, { %marcdta });
    if ($format eq 'Marc') {
 	    $dtarec .= CGIHelper::Dta2Output("100", "1", " ", %marcdta);
    }
 	}

  if ($format eq 'Marc') {
 	  @MRFields = ();
  }
 	my $i = 0;
 	$i = 1 if (defined($record{firstauthor}));
 	while (defined($record{"$i-au"})) {
 		my %marcdta = ();
		$austr .= $record{"$i-au"} . " ; ";
 	 	$marcdta{a} = $record{"$i-au"};
 	 	$marcdta{b} = "$b";
    $b++;
 		$i++;
 		push (@MRFields, { %marcdta });
 	}
 	while (defined($record{"$i-book-editor"})) {
 		my %marcdta = ();
		$austr .= $record{"$i-book-editor"} . " ; ";
 	 	$marcdta{a} = $record{"$i-book-editor"};
 	 	$marcdta{b} = "$b";
    $b++;
 	 	$marcdta{e} = "Other";
 		$i++;
 		push (@MRFields, { %marcdta });
 	};
  if (defined($record{"other"}) && $record{"other"} ne "") { # Avoid warning
	  for (my $i=0 ; $i < scalar(@{$record{"other"}}); $i++) {
	 		my %marcdta = ();
			$austr .= $record{"other"}[$i] . " ; ";
	 	 	$marcdta{a} = $record{"other"}[$i];
	 	 	$marcdta{b} = "$b";
	    $b++;
	 	 	$marcdta{e} = $record{"other-func"}[$i];
	 		push (@MRFields, { %marcdta });
	    $j++;
	  } ;
  };	  

 	$dtarec .= CGIHelper::DtaR2Output("700", "1", " ", @MRFields);
  if ($format ne "Marc") {
	  $marcdta{"a"} = $austr;
 	  $dtarec .= CGIHelper::Dta2Output("100", "1", " ", %marcdta);
  }
 
 	if (defined($record{title})) {
 		my %marcdta = ();
 	 	$marcdta{a} = "$record{title}";
 		$dtarec .= CGIHelper::Dta2Output("245", " ", " ", %marcdta);
 	}

 	if (defined($record{edition})) {
 		my %marcdta = ();
 	 	$marcdta{a} = "$record{edition}";
 		$dtarec .= CGIHelper::Dta2Output("250", " ", " ", %marcdta);
 	}
 
 	%marcdta = ();
 	if (defined($record{extent})) {
 	 	$marcdta{a} = "$record{extent}";
 	}
 	if (defined($record{illustration})) {
 	 	$marcdta{c} = "$record{illustration}";
 	}
 	$dtarec .= CGIHelper::Dta2Output("300", " ", " ", %marcdta);

	# We got conference infos from CrossRef, this gives us 
	# a handle to write 111. We already did that in creation of
	# $confdta, so just pass it along.
	if ($record{SRC} =~ m/CrossRef Conference/) {
		 @MRFields = ();
		 push (@MRFields, { %confdta });
		 $masterta  .= CGIHelper::DtaR2Output("111", "2", " ", @MRFields);
		 $dtarec    .= CGIHelper::DtaR2Output("111", "2", " ", @MRFields);
		 $dtarec    .= CGIHelper::Dta2Output("111", "2", " ", %confdta);
     my %date = {};
     ($beg, $end) = split(/ - /, $confdta{d});
     $date{dcs} = $beg;
     $date{dce} = $end;
		 $dtarec    .= CGIHelper::Dta2Output("111", "2", " ", %date);
	}

  %marcdta = ();
 	if (defined($record{place})) {
 	 	$marcdta{a} = "$record{place}";
 	}
 	if (defined($record{publisher})) {
 	 	$marcdta{b} = "$record{publisher}";
 	}
 	if (defined($record{bookplace})) {
 	 	$marcdta{a} = "$record{bookplace}";
 	}
 	if (defined($record{bookpublisher})) {
 	 	$marcdta{b} = "$record{bookpublisher}";
 	}
 	if (defined($record{bookyear})) {
 	 	$marcdta{c} = "$record{bookyear}";
 	}
 	if (defined($record{year})) {
		$marcdta{c} = "$record{year}";
	}
 	$dtarec .= CGIHelper::Dta2Output("260", " ", " ", %marcdta);

  %marcdta = ();
	if (defined($record{bookseries})) {
 	 	$marcdta{a} = "$record{bookseries}";
 	}
	if (defined($record{bookvol})) {
 	 	$marcdta{v} = "$record{bookvol}";
 	}
 	$dtarec .= CGIHelper::Dta2Output("490", " ", " ", %marcdta);
 
 
 	if (defined($record{comment})) {
 		my %marcdta = ();
 	 	$marcdta{a} = "$record{comment}";
 		$dtarec .= CGIHelper::Dta2Output("500", " ", " ", %marcdta);
 	}
 	if (defined($record{hsv1})) {
 		my %marcdta = ();
		my ($univ, $degree, $year) = split(/, /, $record{hsv1});
		my ($hsv, $place)          = split(/@/, $record{hsv2});

 	 	$marcdta{a} = "$record{hsv2}, $record{hsv1}";
 	 	$marcdta{a} =~ s/@//;
		$marcdta{b} = $degree;
		$marcdta{c} = "$univ $place";
		$marcdta{d} = $year;
 		$dtarec .= CGIHelper::Dta2Output("502", " ", " ", %marcdta);
 	}
 
	if ($mode ne "thin") {
		 if (defined($record{abstract})) {
			 %marcdta = ();
			 $marcdta{a} = "$record{abstract}";
			 $dtarec .= CGIHelper::Dta2Output("520", " ", " ", %marcdta);
		 }
	}

	@MRFields = ();
  $i = 0;
  foreach $fa (@{$record{"FundingAgency"}}) {
    my @grants = split(/\t/, $record{"GrantNo"}[$i]) if (defined($record{"GrantNo"}[$i]));
    foreach $g (@grants) {
	  	my %marcdta = ();
      $marcdta{"0"} = "G:($fa)$g";
      $marcdta{"0"} =~ s/ //g;
	  	$marcdta{"a"} = "$fa: $g";
	  	$marcdta{"c"} = $g;
	  	$marcdta{"2"} = $fa;
	    push (@MRFields, { %marcdta });
    }
    $i++;
  }
 	$dtarec .= CGIHelper::DtaR2Output("536", " ", " ", @MRFields);
 
 	if (defined($record{SRC})) {
 		%marcdta = ();
 	 	$marcdta{a} = "Dataset connected to $record{SRC}";
 		$dtarec .= CGIHelper::Dta2Output("588", " ", " ", %marcdta);
 	}

	if ($mode ne "thin") {
		 
		 # TODO Check why this does not work
		 if (defined($record{LCSH})) {
				@MRFields = ();
				foreach my $t (@{$record{LCSH}}) {
					 %marcdta = ();
					 $marcdta{"a"} = $t;
					 push (@MRFields, { %marcdta });
				}
				$dtarec .= CGIHelper::DtaR2Output("650", " ", "0", %marcdta);
		 }

		 if (defined($record{MeSH})) {
				@MRFields = ();
				foreach my $t (@{$record{MeSH}}){
					my %marcdta = ();
					$marcdta{"a"} = $t;
					$marcdta{"2"} = "MeSH";
					push (@MRFields, { %marcdta });
				}
				$dtarec .= CGIHelper::DtaR2Output("650", " ", "2", @MRFields);
		 }
 	
		 @MRFields = ();
		 foreach my $t (@{$record{InspecKW}}){
			 my %marcdta = ();
			 $marcdta{"a"} = $t;
			 $marcdta{"2"} = "Inspec";
			 push (@MRFields, { %marcdta });
		 }
 
		 $i=0;
		 foreach my $t (@{$record{Chemicals}}){
			 my %marcdta = ();
			 $marcdta{"a"} = $record{Chemicals}[$i];
			 $marcdta{"0"} = $record{CAS}[$i]        if ($record{CAS}[$i] ne 0);
			 $marcdta{"2"} = "NLM Chemicals";
			 push (@MRFields, { %marcdta });
			 $i++;
		 }
		 $dtarec .= CGIHelper::DtaR2Output("650", " ", "7", @MRFields);

		 @MRFields = ();
		 if (defined($record{ID})) {
				my @woskws = split(/; /, $record{ID});
				foreach my $t (@woskws){
					%marcdta = ();
					$marcdta{a} = "$t";
					$marcdta{2} = "Author";
					push (@MRFields, { %marcdta });
				}
				$dtarec .= CGIHelper::DtaR2Output("653", "2", "0", @MRFields);
		 }

	}

 	if (defined($record{url})) {
 		%marcdta = ();
 	 	$marcdta{u} = $record{url};
 		$dtarec .= CGIHelper::Dta2Output("856", "4", " ", %marcdta);
 	}
 
 	if (defined($record{wostype})) {
 		my %marcdta = ();
 	 	$marcdta{"a"} = $record{wostype};
 	 	$marcdta{"2"} = "WoSType";
		$dtarec .= CGIHelper::Dta2Output("650", " ", "7", %marcdta);
 	}
 
 	#--------------------------------------------------
 	# Write out bibliographic reference:
 	# New field should be 773 according to CERN/Annette. This also
 	# preserves import data in 440.
	if (not (defined($record{ppn}))) {
		 my $doi    = "";
		 my $volume = "";
		 my $issue  = "";
		 my $page   = "";
		 my $pages  = "";
		 
		 $doi    = $record{doi}    if (defined($record{doi}));
		 $volume = $record{volume} if (defined($record{volume}));
		 $issue  = $record{issue}  if (defined($record{issue}));
		 $page   = $record{pages}  if (defined($record{pages}));
		 $pages  = $record{pages}  if (defined($record{pages}));

		 my $citation = "";
		 $citation .= "Vol. $volume|" if (defined($volume)) and ("$volume" ne "");
		 $citation .= "no. $issue|"   if (defined($issue)) and ("$issue" ne "");
		 $citation .= "p. $page|"     if (defined($page)) and ("$page" ne "");
		 $citation =~ s/\|/, /g;
		 $citation =~ s/, $//;
		 

		 # Write 773 only if the journal was resolved properly and we have an
		 # ID for it, otherwise use the deprecated 440 to keep the reference
		 # for later rewriting.
		 if (defined($record{zdbid})) {
				%marcdta = ();
				$marcdta{"0"} = $record{zdbid};
				$marcdta{"a"} = $doi;
				$marcdta{"g"} = $citation;
				$marcdta{"n"} = $issue;
				$marcdta{"c"} = $pages;#ebv-page range is the c field, not p
        $marcdta{"q"} = $volume if (defined($volume)) and ("$volume" ne "");
        $marcdta{"q"} .= ":$issue" if (defined($issue)) and ("$issue" ne "");
        $marcdta{"q"} .= "<$pages" if (defined($pages)) and ("$pages" ne "");
				$marcdta{"p"} = $record{journal};
				$marcdta{"v"} = $volume;
				$marcdta{"y"} = $record{year};
				if ($record{issn} ne "") {
					$marcdta{"x"} = $record{issn};
				}
				$dtarec .= CGIHelper::Dta2Output("773", " ", " ", %marcdta);
		 } else {
				# Write all 440 subfields to I440__ they are passed along
				# only
				my @MRFields = ();
				my %marcdta = ();
				$marcdta{"a"} = $doi          if (defined($doi)      and ("$doi"      ne ""));
				$marcdta{"g"} = $citation     if (defined($citation) and ("$citation" ne ""));
				$marcdta{"n"} = $issue        if (defined($issue)    and ("$issue"    ne ""));
				$marcdta{"p"} = $pages        if (defined($pages)    and ("$pages"    ne ""));
        $marcdta{"q"} = $volume       if (defined($volume)   and ("$volume"   ne ""));
        $marcdta{"q"} .= ":$issue"    if (defined($issue)    and ("$issue"    ne ""));
        $marcdta{"q"} .= "<$pages"    if (defined($pages)    and ("$pages"    ne ""));
				$marcdta{"v"} = $volume       if (defined($volume)   and ("$volume"   ne ""));
				$marcdta{"y"} = $record{year} if (defined($record{year}) and ($record{year} ne ""));
        if (defined($record{issn})) {
           if ($record{issn} ne "") {
             $marcdta{"x"} = $record{issn};
           }
        }
        # Some fields are in order for 773 as well, they should be
        # visible for the user to edit them. Probably, he provides us
        # with a valid journal?
        if ((keys %marcdata) > 0) {
				   $dtarec .= CGIHelper::Dta2Output("773", " ", " ", %marcdta);
        }

				@MRFields = ();
        if ((keys %marcdata) > 0) {
           $marcdta{"p"} = $record{journal} if (defined($record{journal}));
           push (@MRFields, { %marcdta });
           $dtarec .= CGIHelper::DtaR2Output("440", " ", " ", @MRFields);
        }
		 }
	}	

	if (defined($record{statkeys}) and ($record{statkeys} ne "")) {
		if ($format eq "Marc") {
				# The input needs to be parsed for Marc as we need to identify
				# the subfields of this "string". It is in fact valid JSON,
				# just the " are escaped. => Remove this, parse it and then
				# handle it as usual.
				my $json = new JSON;
				my $txt = $record{statkeys};
				$txt =~ s/\\//g;
				my $json_text =
				$json->allow_nonref->utf8->relaxed->escape_slash->loose->allow_singlequote->allow_barekey->decode($txt);
				@MRFields = ();
				foreach my $skey (@{$json_text}) {
					%marcdta = ();
					$marcdta{a} =  $skey->{a};
					$marcdta{b} =  $skey->{b} if (defined($skey->{b}));
					$marcdta{0} =  $skey->{0};
					$marcdta{2} =  $skey->{2};
					push (@MRFields, { %marcdta });
				}
				$dtarec .= CGIHelper::DtaR2Output("915", " ", " ", @MRFields);
			} else {
				# we get it properly escaped if we need JSON, no need to
				# rehandle it.
				$dtarec .= '  "I915__"  : "' . $record{statkeys} . '",' . "\n";
			}
 	}


	if ($format eq "Marc") {
		 $dtarec .= '</record>' . "\n";
		 $dtarec .= '</collection>' . "\n";
	} else {
     my $ISBD = "";
     $ISBD .= $record{title};
     $ISBD .= " / ";
     if (defined($record{firstauthor})) {
       $ISBD .=  $record{firstauthor};
     } else {
       $ISBD .=  $record{"0-au"};
     }
     $ISBD .= " ; ";
     $ISBD .= $record{journal}   . " " if (defined($record{journal})); 
     $ISBD .= $record{volume}    . " "   if(defined($record{volume}   ));
     $ISBD .= $record{pages}     . " ; " if(defined($record{pages}    ));
     $ISBD .= $record{place}     . " : " if(defined($record{place}    ));
     $ISBD .= $record{publisher} . ", "  if(defined($record{publisher}));
     $ISBD .= $record{year}      . " ; " if(defined($record{year}     ));
     $ISBD .= $record{doi}       . " ; " if(defined($record{doi}      ));
     $ISBD .= $record{isbn}              if(defined($record{isbn}     ));
     $ISBD =~ s/\n\r?/ /g;
     $ISBD =~ s/"/'/g;
     $ISBD =~ s/\\/\\\\/g;
     $dtarec .= ' "SHORTTITLE" : "' . $ISBD . '",' . "\n"; 

     my %duprecs = CheckID4Dupes(@uniqueIDs);
     my $dupes = "";
     if (keys(%duprecs) > 0) {
        $dupes = ' "DUPES" : "';
        if (keys(%duprecs) > 0) {
           for my $recid (sort(keys(%duprecs))) {
             $dupes .= "$recid, "; 
           }
           $dupes .= '", ';
        }
     }
     $dtarec .= $dupes;
		 $dtarec .= "},\n";
	}
	return($dtarec);
}


1;
__END__

