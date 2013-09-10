#!/usr/bin/perl -w
#=========================================================================
#
#    JournalMatch.pl
#
#	   Fetch entry from publications database and try to match it with
#	   ZDB entry to add ZDB-ID as identifier.
#
#    $Id: $
#    Last change: <Do, 2012/11/15 16:56:58 cdsware zb0035.zb.fz-juelich.de>
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

use Encode;
use IO::Handle;
use LWP::UserAgent;
use arwagner::MarcXML;
use arwagner::crossref;
use File::Path;

# Content enrichment
use arwagner::enrich;

use Storable qw(store retrieve freeze thaw dclone);
*STDOUT->autoflush(1);    # Unbuffered screen IO

my $useragent = "Perl/5";

#--------------------------------------------------
# Invenio Connection
my $invenio    = "http://juser.fz-juelich.de/search?action_search=Suchen";
my $invenioZDB = "http://juser.fz-juelich.de/search?action_search=Suchen";
$invenio    = "http://zb0035.zb.kfa-juelich.de/search?action_search=Suchen";
$invenioZDB = "http://zb0035.zb.kfa-juelich.de/search?action_search=Suchen";
my $zdbcoll    = "cc=Periodicals";
my $issnsearch = "f=issn";
my $ofzdb      = "of=zzzdb";
my $term       = "p";
my $number     = 100;    # limitation in invenio: not more than 200 at once
my $noofitems  = "rg=$number";
my $startrec   = "jrec=";
my $issn = "1089-4918";

my $vdbcoll    = "cc=VDB";
# $vdbcoll = "cc=JournalArticle";
my $titsearch  = "f=title";
my $ofvdb      = "of=zzvdb";

my $vdbterm = '980__a:"journal"';
# my $vdbterm = "I:(DE-Juel1)IEK-4-20101013";
# $vdbterm = '9201_0:"I:(DE-Juel1)IEK-4-20101013" and 260__c:"2011"';
# $vdbterm = "000300580900009";
# $vdbterm = "recid:132309";
# $vdbterm = "recid:59995";
# $vdbterm = "recid:62982";
my $issnquery = "$invenioZDB&$zdbcoll&$issnsearch&$ofzdb&$term=$issn&$noofitems";

my $firstrec = 1;
my $finished = 0;
my %doneid   = ();

my %doi2utlst = ();
my %ut2doilst = ();
my $DOI2WOS   = "DOI2WOS.txt";

if (-e $DOI2WOS) {
  print "Reading DOI <-> WOS concordance.\n";
  open(IN, "<$DOI2WOS");
  my $line = <IN>;
  while($line = <IN>) {
    $line =~ s/\n//;
    my ($DOI, $UT) = split(/\t/, $line);
    $doi2utlst{$DOI} = $UT;
    $ut2doilst{$UT} = $DOI;
  }
  close(IN);
}

open(OUT, ">>notfound.issn");
open(UT2DOI, ">>ut2doi.lst");
open(MISS, ">>missing.lst");
*OUT->autoflush(1);    # Unbuffered screen IO
*UT2DOI->autoflush(1);    # Unbuffered screen IO

my $marcupdate = "/tmp/MarcUpdate";
my $pmcprefix  = "http://www.ncbi.nlm.nih.gov/pmc/articles";

mkpath($marcupdate);

while($finished == 0) {

   my $vdbquery = "$invenio&$vdbcoll&f=&$ofvdb&$term=$vdbterm&$noofitems&$startrec$firstrec";
   print "$vdbquery\n";



   #======================================================================
   my $ua = new LWP::UserAgent;
   $ua->agent("$useragent");
   $ua->env_proxy;

   my $request   = new HTTP::Request(GET,$vdbquery);
   my $response  = $ua->request($request);
   my $list      = $response->content();
   my @lines = split(/\n/, $list);
   foreach $l (@lines) {
      print "$l\n";
      my ($artid, $vdbid, $issn, $jid, $journal, 
          $vol, $iss, $pag, $idents, $au, $year) = split(/\|/, $l);
      $vol = '' if $vol =~ /^\.$/;

      if (-e "$marcupdate/$artid.xml") {
         print "Already done: $artid\n";
         $doneid{$artid}++;
         if ($doneid{$artid} > 1) {
           $finished = 1;
         }
      } elsif (not(defined($doneid{$artid}))) {
         $doneid{$artid} = 1;
      } else {
         $finished = 1;
      }
      if ($finished == 0) {
         my $query = "";

         $doneid{$artid} = 1;
         next if -e "$marcupdate/$artid.xml";

         my @identifier = split(/_:_/, $idents);
         my @authors    = split(/ ; /, $au);
         my $doi        = "";
         my $ut         = "";
         if (    $issn eq '' and $jid eq '' and $journal eq ''
             and $vol eq ''  and $pag eq '' and $idents eq '') {
           print "No extensible data found.\n";
           next;
         }

         print "----> $artid = $vdbid\n";
         next if ($vdbid eq '');       # only touch migrated datasets.
         my %record     = ();
         foreach $i (@identifier) {
            if ($i =~ m/=DOI/) {
               $doi = $i;
               $doi =~ s/=DOI//g;
               print "   DOI present: $doi\n";
            }
            if (($i =~ m/WOS/) or ($i =~ m/ISI/)) {
               $ut = $i;
               $ut =~ s/=ISI//g;
               $ut =~ s/=WOS//g;
               $ut =~ s/ISI://;
               $ut =~ s/WOS://;
               print "   UT present: $ut\n";
            }
         }
         if (($ut eq "") && ($doi ne "")) {
           if (defined($doi2utlst{$doi})) {
              $ut = $doi2utlst{$doi};
              $ut =~ s/=ISI//g;
              $ut =~ s/ISI://;
              $ut =~ s/WOS://;
              print "   Added missing UT: $ut\n";
           }
         }
         if (($doi eq "") && ($ut ne "")) {
           if (defined($ut2doilst{"WOS:$ut"})) {
              $doi = $ut2doilst{"WOS:$ut"};
              print "   Added missing DOI: $doi\n";
           }
         }

         # Try to enrich if a doi is present
         if ($doi ne "") {
            print "   Calling CrossRef by DOI\n";
            %record = crossref::DOI2bib($doi);
            if ($issn eq "") {
               if (defined($record{pissn}) and ($record{pissn} ne "")) {
                  $issn = $record{pissn}
               } elsif (defined($record{eissn}) and ($record{eissn} ne "")) {
                  $issn = $record{eissn}
               }
            }
         }

         #--------------------------------------------------
         # try to resolve a doi. Do this after ZDB association as this
         # might result in a usable ISSN which is more reliable then journal
         # names @crossref
         $au = "";
         if (defined($authors[0])) {
            $au = $authors[0];
            $au =~ s/,.*$//;
         }
         if ($doi eq "") {
            if ($issn ne "") {
               print "   Initiate CrossRef bibliographic query using $issn.\n";
               my $i = $issn;
               $i =~s/-//g;
               %record = crossref::CrossRefQuery($i, "", 
                  $au, $vol, $iss, $pag, $year, "", "");
            } else {
               print "   No ISSN: initiate CrossRef bibliographic query.\n";
               %record = crossref::CrossRefQuery("", $journal,
                  $au, $vol, $iss, $pag, $year, "", "");
               $issn = $record{issn} if (defined($record{issn}));
            }
         }

         #--------------------------------------------------
         # Try to match record to ZDB
         if ($issn ne "") {
            # Add a probably missing hyphen
            if (not ($issn =~ /-/)) {
               my $i1 = substr($issn, 0, 4);
               my $i2 = substr($issn, 4, 4);
               $issn = $i1 . "-" . $i2;
            }
            $query = "$invenioZDB&$zdbcoll&$issnsearch&$ofzdb&$term=$issn";
         } else {
            $query = "$invenioZDB&$zdbcoll&$titsearch&$ofzdb&$term=$journal";
         }
         print "   Get Journal Info (Invenio)\n";
         my $ua = new LWP::UserAgent;
         $ua->agent("$useragent");
         $ua->env_proxy;

         my $request   = new HTTP::Request(GET,$query);
         my $response  = $ua->request($request);

         my @lines = split(/\n/, $response->content());
         my ($inveniojournalid, $zdbid, $jtitle, $issnlst, $idlst,
            $statjson, $journalddc, $place, $publisher) = '';
         if ($#lines == 0) {
            ($inveniojournalid, $zdbid, $jtitle, $issnlst, $idlst,
            $statjson, $journalddc, $place, $publisher) = split(/\|/, $response->content());
            $publisher =~ s/\n//;
            my @issns = split(/ /, $issnlst);

            if ($issn eq "") {
               $issn = $issns[0] if (defined($issns[0]));
            }
         }

         if (not defined($jtitle) or ($jtitle eq '')) {
         # we got a journal title from crossref but were not able to
         # match it against our local db. Store it here but we need to
         # generate the journal record later on.
            if (defined($record{journal}) and ($record{journal} ne "")) {
              $jtitle = $record{journal};
            }
            else {
               $jtitle = 'N/A';
            }
         }

         my $citation = "";
         my $volume   = $vol;
         my $issue    = "";
         my $page     = $pag;

         my %enrichment = ();
         print "   Enriching Record:\n";
         %enrichment = enriche::enriche($doi, $ut);
         $enrichment{ut} = $ut;

         if (not(defined($zdbid)) or ($zdbid eq "")) {
           print OUT "$issn\t$artid\t$vdbid\n";
           $zdbid  = "--NOT MATCHED--";
         }

         print UT2DOI "$vdbid\t$artid\t$doi\t$ut\n";

         $doi    = $record{doi}    if (defined($record{doi   }) and ($doi   ne ""));
         $volume = $record{volume} if (defined($record{volume}) and ($vol   ne ""));
         $issue  = $record{issue}  if (defined($record{issue }) and ($issue ne ""));
         $page   = $record{page}   if (defined($record{page  }) and ($pag   ne ""));

         $citation .= "Vol. $volume|" if ($volume  ne "");
         $citation .= "no. $issue|"   if ($issue   ne "");
         $citation .= "p. $page|"     if ($page    ne "");
         $citation =~ s/\|/, /g;
         $citation =~ s/, $//;
         #--------------------------------------------------
         # Generate the update XML
         my $xml = "";
         $xml .= '<?xml version="1.0" encoding="UTF-8"?>' . "\n";
         $xml .= '<collection xmlns="http://www.loc.gov/MARC21/slim">' . "\n";
         $xml .= "<record>\n";
         ## It's better to do the update by vdbid in 970
         ## $xml .= MarcXML::GetMarcControlfield("001" , $artid);
         %marcdta = ();
         $marcdta{a} = "$vdbid";
         $xml .= MarcXML::MarcField("970", " ", " ", %marcdta);

         my $marcdta = ();
         #--------------------------------------------------
         # Write the enrichtments
         if (defined($enrichment{pmid})) {
           %marcdta = ();
           $marcdta{a} = "pmid:$enrichment{pmid}";
           $marcdta{2} = "pmid";
           $xml .= MarcXML::MarcField("024", "7", " ", %marcdta);
         }
         if ((defined($enrichment{pmc})) and ($enrichment{pmc} ne "")){
           %marcdta = ();
           $marcdta{a} = "pmc:$enrichment{pmc}";
           $marcdta{2} = "pmc";
           $xml .= MarcXML::MarcField("024", "7", " ", %marcdta);


           # If there is a PMC, there is also a fulltext available
           %marcdta = ();
           $marcdta{u} = "$pmcprefix/$enrichment{pmc}";
           $marcdta{2} = "Pubmed Central";
           $xml .= MarcXML::MarcField("856", "7", " ", %marcdta);
         }

         if (defined($enrichment{inspecid})) {
           %marcdta = ();
           # inspecid is prefixed with inh: already
           $marcdta{a} = "$enrichment{inspecid}";
           $marcdta{2} = "inh";
           $xml .= MarcXML::MarcField("024", "7", " ", %marcdta);
         }
         if (defined($enrichment{doi}) and ($enrichment{doi} ne "")) {
           %marcdta = ();
           $marcdta{a} = "$enrichment{doi}";
           $marcdta{2} = "DOI";
           $xml .= MarcXML::MarcField("024", "7", " ", %marcdta);
         }
         if (defined($ut) and ($ut ne '')) {
           %marcdta = ();
           # inspecid is prefixed with inh: already
           $marcdta{a} = "WOS:$ut";
           $marcdta{2} = "WOS";
           $xml .= MarcXML::MarcField("024", "7", " ", %marcdta);
         }

         if (defined($enrichment{lang})) {
           $xml .= MarcXML::GetMarc("041", " ", " ", "a", "$enrichment{lang}")
         }

         if (defined($journalddc)) {
            if ($journalddc ne '') {
               $xml .= MarcXML::GetMarc("082", " ", " ", "a", "$journalddc")
            }
         }

         if (defined($year)) {
           %marcdta = ();
           # inspecid is prefixed with inh: already
           $marcdta{a} = $place;
           $marcdta{b} = $publisher;
           $marcdta{c} = $year;
           $xml .= MarcXML::MarcField("260", " ", " ", %marcdta);
         }

         foreach my $t (@{$enrichment{InspecSC}}){
           %marcdta = ();
           $marcdta{a} = "$t";
           $marcdta{2} = "Inspec";
           $xml .= MarcXML::MarcField("084", " ", " ", %marcdta);
         }

         if (defined($enrichment{abstract})) {
           $xml .= MarcXML::GetMarc("520", " ", " ", "a", "$enrichment{abstract}");
         }

         if (defined($enrichment{FundAckTxt})) {
           my %marcdta = ();
           $marcdta{a} = "$enrichment{FundAckTxt}";
           $xml .= MarcXML::MarcField("500", " ", " ", %marcdta);
         }

         ## # 536 is coupled to 9131_ so this is not that trivial...
         ## $i = 0;
         ## foreach $fa (@{$enrichment{"FundingAgency"}}) {
         ##   my @grants = split(/\t/, $enrichment{"GrantNo"}[$i]) if (defined($enrichment{"GrantNo"}[$i]));
         ##   foreach $g (@grants) {
         ##     my %marcdta = ();
         ##     $marcdta{"0"} = "G:($fa)$g";
         ##     $marcdta{"0"} =~ s/ //g;
         ##     $marcdta{"a"} = "$fa: $g";
         ##     $marcdta{"c"} = "$g";
         ##     $marcdta{"2"} = "$fa";
         ##     $xml .= MarcXML::MarcField("536", " ", " ", %marcdta);
         ##   }
         ##   $i++;
         ## }

         if (defined($enrichment{SRC})) {
           $xml .= MarcXML::GetMarc("588", " ", " ", "a", "Dataset connected to $enrichment{SRC}");
         }

         foreach my $t (@{$enrichment{MeSH}}){
           %marcdta = ();
           $marcdta{a} = "$t";
           $marcdta{2} = "MeSH";
           $xml .= MarcXML::MarcField("650", " ", "2", %marcdta);
         }
         
         foreach my $t (@{$enrichment{InspecKW}}){
           %marcdta = ();
           $marcdta{a} = "$t";
           $marcdta{2} = "Inspec";
           $xml .= MarcXML::MarcField("650", " ", "7", %marcdta);
         }

         my $i=0;
         foreach my $t (@{$enrichment{Chemicals}}){
           %marcdta = ();
           $marcdta{a} = $enrichment{Chemicals}[$i];
           $marcdta{0} = $enrichment{CAS}[$i];
           $marcdta{2} = "NLM Chemicals";
           $xml .= MarcXML::MarcField("650", " ", "7", %marcdta);
           $i++;
         }

         if (defined($enrichment{SC})) {
           my @wossc = split(/; /, $enrichment{SC});
           foreach my $t (@wossc){
              %marcdta = ();
              $marcdta{a} = "$t";
              $marcdta{2} = "WoS";
              $xml .= MarcXML::MarcField("084", " ", " ", %marcdta);
           }
         }
         if (defined($enrichment{DE})) {
            # author supplied keywords
           my @woskw = split(/; /, $enrichment{DE});
           foreach my $t (@woskw){
              %marcdta = ();
              $marcdta{a} = "$t";
              $marcdta{2} = "Author";
              $xml .= MarcXML::MarcField("653", "2", "0", %marcdta);
           }
         }
         #-# Do not add WOS autogenerated keywords
         #-# if (defined($enrichment{ID})) {
         #-#  	@woskw = split(/; /, $enrichment{ID});
         #-#  	foreach my $t (@woskw){
         #-#  		 %marcdta = ();
         #-#  		 $marcdta{a} = "$t";
         #-#  		 $marcdta{2} = "WoS+";
         #-#  		 $xml .= MarcXML::MarcField("653", "2", "0", %marcdta);
         #-#  	}
         #-# }


         if (defined($enrichment{wostype})) {
           $xml .= MarcXML::GetMarcDatafield("650", " ", "7");
           $xml .= MarcXML::GetMarcSubfield("a", "$enrichment{wostype}");
           $xml .= MarcXML::GetMarcSubfield("2", "WoSType");
           $xml .= MarcXML::EndMarcDatafield();
         }

         #--------------------------------------------------
         # Write out bibliographic reference:
         # New field should be 773 according to CERN/Annette. This also
         # preserves import data in 440.
         %marcdta = ();
         $marcdta{a} = $doi      if (defined($doi      ) and ($doi       ne ""));
         $marcdta{0} = $zdbid    if (defined($zdbid    ) and ($zdbid     ne ""));
         $marcdta{t} = $jtitle   if (defined($jtitle   ) and ($jtitle    ne ""));
         $marcdta{v} = $volume   if (defined($volume   ) and ($volume    ne ""));
         $marcdta{n} = $issue    if (defined($issue    ) and ($issue     ne ""));
         $marcdta{y} = $year     if (defined($year     ) and ($year      ne ""));
         $marcdta{g} = $citation if (defined($citation ) and ($citation  ne ""));
         $marcdta{p} = $page     if (defined($page     ) and ($page      ne ""));
         $marcdta{q} = '';
         if (defined($volume) and ($volume ne "")) {
            $marcdta{q} .= "$volume"
         }
         if (defined($issue) and ($issue ne "")) {
            if ($marcdta{q} ne "") {
               $marcdta{q} .= ":";
            } 
            $marcdta{q} .= $issue;
         }
         if (defined($page) and ($page ne "")) {
            if ($marcdta{q} ne "") {
               $marcdta{q} .= "<";
            } 
            $marcdta{q} .= $page;
         }
         if ($issn ne "") {
           $marcdta{x} = $issn;
         }

         if (($jtitle  eq "") or 
            ($volume   eq "") or 
            ($year     eq "") or 
            ($citation eq "") or 
            ($page     eq "") ) {
            print MISS "$doi\t$vdbid\t$zdbid\t$jtitle\t$volume\t$issue\t$year\t$page\t$issn\n";
         }

         $xml .= MarcXML::MarcField("773", " ", " ", %marcdta);

         # we are rewriting old data => transfer old statids only.
         if (defined($statjson)) {
            if ($statjson =~ m/StatID:\(DE-HGF\)0010/) {
               %marcdta = ();
               $marcdta{a} = "JCR/ISI refereed";
               $marcdta{0} = "StatID:\(DE-HGF\)0010";
               $xml .= MarcXML::MarcField("915", " ", " ", %marcdta);
            }

            if ($statjson =~ m/StatID:\(DE-HGF\)0020/) {
               %marcdta = ();
               $marcdta{a} = "No peer review";
               $marcdta{0} = "StatID:\(DE-HGF\)0020";
               $xml .= MarcXML::MarcField("915", " ", " ", %marcdta);
            }

            if ($statjson =~ m/StatID:\(DE-HGF\)0030/) {
               %marcdta = ();
               $marcdta{a} = "Peer review";
               $marcdta{0} = "StatID:\(DE-HGF\)0030";
               $marcdta{2} = "StatID";
               $xml .= MarcXML::MarcField("915", " ", " ", %marcdta);
            }
         }

         # Conclude the record and encode in utf-8
         $xml .= "</record>\n";
         $xml .= "</collection>\n";
         $xml = encode("utf8", $xml);

         print "\n\n";

         open(XML, ">$marcupdate/$artid.xml");
         print XML "$xml\n";
         close(XML);

         sleep(1)
      }
  }
  $firstrec += $number;
}
close(OUT);
close(UT2DOI);
