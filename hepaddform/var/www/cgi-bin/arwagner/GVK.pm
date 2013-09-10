package GVK;
#=========================================================================
#
#    GVK.pm
#
#		 Use SRU to access GVK union catalogue and return a record for a
#		 given book.
#
#    $Id: $
#    Last change: <Di, 2012/08/21 15:55:34 cdsware zb0027.zb.kfa-juelich.de>
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

# Connect to GVK Union Catalogue
use PICA::Record;     #   \ for UnAPI
use LWP::Simple;      #   / 
use PICA::Source;     #   for SRU
use PICA::SRUSearchParser;

use Encode;
use IO::Handle;

use arwagner::arwagner;
use arwagner::CGIHelper;

*STDOUT->autoflush(1);    # Unbuffered screen IO

@ISA    = ('Exporter');
@EXPORT = qw();

#--------------------------------------------------
my $gvk    = "http://gso.gbv.de/sru/DB=2.1/";
my $gbvsru = PICA::Source->new( SRU => $gvk );

#======================================================================
#----------------------------------------------------------------------
my $record_handler = sub {
    my $record = shift;
    # filter and/or process records as you like
    return $record; # don't drop records, so you can later access them
};

#----------------------------------------------------------------------
# TODO This procedure needs improvement.
sub CreateRecord($) {
	my ($record) = @_;
	my %gvkrec = ();
	if (defined($record)) {
		my $commentstr = "";
		## # print $record->normalized();
		## # print $record->local->normalized();
		## # print $record->copy->normalized();
		## if ($record->subfield('021A$x1')) {
		##   # a book within a book of some kind (j-records)
		##   $bibtex .= "\@InBOOK{" . $record->subfield('003@$0') . ",\n";
		## }
		## else {
		##   # a real book itself
		##   $bibtex .= "\@BOOK{" . $record->subfield('003@$0') . ",\n";
		## }

		# authors
		$gvkrec{"ppn"} = $record->subfield('003@$0');
		$gvkrec{"SRC"} = "GVK";
		if ($record->subfield('028A$a')) {
			 $gvkrec{"firstauthor"}  = $record->subfield('028A$a') . ", "
															 . $record->subfield('028A$d');
			 $gvkrec{"0-au"}  = $record->subfield('028A$a') . ", "
												. $record->subfield('028A$d');
		}
		for (my $i=1; $i < 10; $i++) {
			if ($record->field("028B/0$i")) {
				my $j = 0;
				if (defined($gvkrec{"0-au"})) {
					$j = $i;
				} else {
					$j = $i-1;
				}
				$gvkrec{"$j-au"} = $record->subfield('028B/0'.$i.'$a') .  ", "
												 . $record->subfield('028B/0'.$i.'$d');
			}
		}

		# other contributing persons
		if ($record->subfield('028C$a')) {
				$gvkrec{"0-editor"} = $record->subfield('028C$a') . ", "
														. $record->subfield('028C$d');
        $j = 1;
		}
		for (my $i=1; $i < 10; $i++) {
			if ($record->field("028C/0$i")) {
				$gvkrec{"$j-editor"} = $record->subfield('028C/0'.$i.'$a') . ", "
														 . $record->subfield('028C/0'.$i.'$d');
        $j++;
			}
		}

    $gvkrec{"other"}      = [];
    $gvkrec{"other-func"} = [];
    my $j = 0;
		if ($record->subfield('028G$a')) {
        $j = 1;
				$gvkrec{"other"}[0]      = $record->subfield('028G$a') . ", "
														     . $record->subfield('028G$d');
        if ($record->subfield('028G$B')) {
          $gvkrec{"other-func"}[0] = $record->subfield('028G$B');
        } else {
				  $gvkrec{"other-func"}[0] = "";
        }
		}
		for (my $i=1; $i < 10; $i++) {
			if ($record->field("028G/0$i")) {
				$gvkrec{"other"}[$j] = $record->subfield('028G/0'.$i.'$a') . ", "
														 . $record->subfield('028G/0'.$i.'$d');
        if ($record->subfield('028G/0'.$i.'$B')) {
				  $gvkrec{"other-func"}[$j] = $record->subfield('028G/0'.$i.'$B');
        }
        $j++;
			}
		}

		## if ($record->subfield('036D$9')) {
		##   # multiple volumes detected place a crossref
		##   $mbw  = $record->subfield('036D$9');
		##   $bibtex .= "   crossref = {" . $mbw . "},\n";
		## }
		## if ($record->subfield('039D$9')) {
		##   # Recension to some book
		##   $mbw  = $record->subfield('039D$9');
		##   $bibtex .= "   crossref = {" . $mbw . "},\n";
		##   # how to do this canonically???
		##   $commentstr = $commentstr . "Rezension; ";
		## }
		if ($record->field('037A')) {
		  my @addcomments = $record->field('037A$a');
		  foreach $comm (@addcomments) {
		 	 $commentstr = $commentstr . "$comm; "
		  }
		}
		if ($record->subfield('046M$a')) {
		 	 $commentstr = $commentstr . $record->subfield('046M$a') . "; "
		}


		if ($record->subfield('021A$a')) {
			 # a normal book has this field set
			 $gvkrec{"title"} = $record->subfield('021A$a');
			 # add the subtitle
			 if ($record->subfield('021A$d')) {
					$gvkrec{"title"} .= " : " . $record->subfield('021A$d');
			 }
			 # strip off the non-sorting char
			 $gvkrec{"title"} =~ s/@//g;
		}

		## if ($record->subfield('021A$x1')) {
		##   # this is a j-record and stores the title in another field
		##   $mbw = $record->subfield('021A$9');
		##   $bibtex .= "   crossref = {" . $mbw . "},\n";

		##   $bibtex .= "   title    = {";
		##   if ($record->subfield('036C$a')) {
		##  	 $bibtex .= $record->subfield('036C$a') . ": ";
		##   }
		##   $bibtex .= $record->subfield('021B$a') . "},\n";
		## }

		## if ($record->subfield('004A$a')) {
		##   $bibtex .= "   howpublished = {" . $record->subfield('004A$a') . "},\n";
		## }

		$gvkrec{"bookplace"}     = $record->subfield('033A$p');
		$gvkrec{"bookpublisher"} = $record->subfield('033A$n');
		$gvkrec{"edition"}       = $record->subfield('032@$a');
		$gvkrec{"pages"}         = $record->subfield('034D$a');
		$gvkrec{"series"}        = $record->subfield('036E$a');
		if (defined($gvkrec{"series"}) and
				(defined($record->subfield('036E$e')))) {
				$gvkrec{"series"}       .= " / ";
				$gvkrec{"series"}       .= $record->subfield('036E$e');
		}
		$gvkrec{"volume"}        = $record->subfield('036E$m');

		if ($record->subfield('037C$a')) {
			 $gvkrec{"hsv1"} = $record->subfield('037C$a');
		}
		if ($record->subfield('037C$b')) {
			 $gvkrec{"hsv2"} = $record->subfield('037C$b');
		}
		
		## if ($record->subfield('036E$l')) {
		##   $bibtex .= "   number = {" . $record->subfield('036E$l') . "},\n";
		## }
		$gvkrec{"language"} = $record->subfield('010@$a');
		$gvkrec{"bookyear"}     = $record->subfield('011@$a');

		# handling 10 and 13 digits ISBN, store both if available
		# Check also for additional ISBN-fields
		if ($record->subfield('004A$A')) {
			 $gvkrec{"isbn"} = $record->subfield('004A$A');
		}
		elsif ($record->subfield('004L$0')) {
			 $gvkrec{"isbn"} = $record->subfield('004L$0');
		}
		if ($record->subfield('004A$0')) {
			 $gvkrec{"sisbn"} = $record->subfield('004A$0');
		}
		elsif ($record->subfield('004B$0')) {
			 $gvkrec{"sisbn"} = $record->subfield('004B$0');
		}

		$gvkrec{"loc"} = $record->subfield('045A$a');
		$gvkrec{"ddc"} = $record->subfield('045F$a');
		$gvkrec{"ddc"} =~ s/[^0-9\.]//g if (defined($gvkrec{ddc}));
		if ($record->subfield('045Q/01$8')) {
		  $gvkrec{"0-bk"} = $record->subfield('045Q/01$8'); 
		}
		if ($record->subfield('045Q/02$8')) {
		  $gvkrec{"1-bk"} = $record->subfield('045Q/02$8'); 
		}
		if ($record->subfield('045Q/03$8')) {
		  $gvkrec{"2-bk"} = $record->subfield('045Q/03$8'); 
		}
		if ($record->subfield('045Q/04$8')) {
		  $gvkrec{"3-bk"} = $record->subfield('045Q/04$8'); 
		}
		if ($record->subfield('045Q/05$8')) {
		  $gvkrec{"4-bk"} = $record->subfield('045Q/05$8'); 
		}

		if ($record->subfield('034M$a') || $record->subfield('037A$a')) {
		  my $illstr = $record->subfield('034M$a');
		  $illstr .= $record->subfield('037M$a') if (defined($record->subfield('037M$a')));
			 $gvkrec{"illustration"} = $illstr;
		}
		#					   $record->subfield('045G$a') . "},\n";
		my @GerKeywords  = $record->field('041A');
		my @LCKeywords   = $record->field('044A');
		my @MESH         = $record->field('044C');
		my @DDBKeywords  = $record->field('044F');
		my @BCKeywords   = $record->field('044G');
		my @Keywords     = $record->field('044K');

		my $i=0;
    ## $8 subfields are interpolated from $9 identifiers
		## foreach $k (@Keywords) {
		##   $gvkrec{"Keywords"}[$i] = $k->subfield("8");
		## 	 $i++;
		## }
		## $i=0;
		## foreach $k (@GerKeywords) {
		##   $gvkrec{"SWD"} = $k->subfield("8");
		## 	$i++;
		## }
		$i=0;
		foreach $k (@DDB) {
		  $gvkrec{"DDB"}[$i] = $k->subfield("a");
			 $i++;
		}
		$i=0;
		foreach $k (@LCKeywords) {
		  $gvkrec{"LCSH"}[$i] = $k->subfield("a");
			 $i++;
		}
		$i=0;
		foreach $k (@BCKeywords) {
		  $gvkrec{"BLLCSH"}[$i] = $k->subfield("a");
			 $i++;
		}
		$i=0;
		foreach $k (@MESH) {
		  $gvkrec{"MeSH"}[$i] = $k->subfield("a");
			 $i++;
		}

		$gvkrec{"comment"} = $commentstr;

		# $bibtex .= "   comment  = {$commentstr},\n";

		if ($record->field('045M/90')) {
		my @rvkother = $record->field('045M/90');
		$i=0;
		for $r (@rvkother) {
			 my $rvk = $r->subfield("a");
			 $gvkrec{"RVK"}[$i] = $rvk;
				 $i++;
			}
		}
		# normally the TOC or something like that.
		if ($record->subfield('009Q$a')) {
			$gvkrec{"url"} = $record->subfield('009Q$a');
		}
	}
	for my $k (keys %gvkrec) {
		# Strip all nonsorting chars from GVK. We can not handle that in
		# websubmit type submissions.
		$gvkrec{$k} =~ s/@//g if (defined($gvkrec{$k}));
	}
	return(%gvkrec);
}
#----------------------------------------------------------------------
sub GVKquery($$$) {
	my ($mode, $limit, $query) = @_;
	my $parser = $gbvsru->cqlQuery( $query, Record => $record_handler, Limit => $limit );
	my %gvkrec = ();
	my @records = $parser->records();
	my $json = "";
	foreach my $r (@records) {
		my %gvkrec  = CreateRecord($r);
		my $label   = "";
		my $recjson = "";

		if ((not defined($gvkrec{"0-au"})) or ($gvkrec{"0-au"} eq "")) {
			$label = $gvkrec{title} . " / " . $gvkrec{"0-editor"} . " (Ed.)";
			$label .= "..." if ($gvkrec{"1-editor"});
		} else {
			$label = $gvkrec{title} . " / " . $gvkrec{"0-au"};
			$label .= "..." if ($gvkrec{"1-au"});
		}
		$label .= " - $gvkrec{edition}" if ($gvkrec{edition} ne "");
		$label .= " - $gvkrec{bookplace} : $gvkrec{bookpublisher},";
		$label .= " $gvkrec{bookyear}";
		my %record = CGIHelper::CopyGVK($mode, %gvkrec);
		$recjson   = CGIHelper::MakeOutput("JSON", $mode, %record);
		$recjson   =~ s/^{//;
		$recjson   =~ s/},$//;


		$json .= "{\n";
		$json .= '"label" : "' . $label . '", '; 
		$json .= "\n";
		$json .= $recjson;
		$json .= "},\n";
	}
	$json = $json;
	return($json);
}

#----------------------------------------------------------------------
sub AUTISearch($$$) {
	my ($mode, $per, $tit) = @_;
	my $limit = 10;
	my $query = "pica.per=$per and pica.tit=$tit";
	return(GVKquery($mode, $limit, $query));
}

#----------------------------------------------------------------------
sub FetchISBN($$) {
	my ($mode, $isbn) = @_;
	my $limit = 10;
	my $query = "pica.isb=$isbn";
	my $json = GVKquery($mode, $limit, $query);
	## print "\n" , "-" x70 , "\n";
	## print $json;
	## print "\n" , "-" x70 , "\n";
	return($json)
}

sub FetchPPN($) {
	my ($ppn) = @_;
	my $record = $gbvsru->getPPN($ppn);
	my %gvkrec = CreateRecord($record);
	return(%gvkrec)
}

1;

__END__

