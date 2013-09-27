package inspire;
#=========================================================================
#
#    inspire.pm
#
#    Simple interface to inspirehep.net using their xm output format.
#
#    $Id: $
#    Last change: <Fr, 2012/06/15 11:18:19 cdsware zb0027.zb.kfa-juelich.de>
#    Author     : M. Köhler adopted form arXiv.pm from Alexander Wagner
#    Language   : Perl
#
#-------------------------------------------------------------------------
#
#    Copyright (C) 2009 by Alexander Wagner, M. Köhler
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

use HGF::Forms::crossref;
use HGF::Forms::HGF;

*STDOUT->autoflush(1);    # Unbuffered screen IO

@ISA    = ('Exporter');
@EXPORT = qw();

#======================================================================

=head1 NAME

Access for inspirehep.net

=cut
#----------------------------------------------------------------------

my $prefix             = "http://inspirehep.net/record/";
my $suffix	       = "/export/xm";
my $useragent       = "arXiv Client";

#----------------------------------------------------------------------
=head2 

Status: unchecked

=cut

#----------------------------------------------------------------------
sub AUString($) {
# Takes a xml node with subfield "a" and possible "i"
# Example 
#<subfield code="a">Dappiaggi, Claudio</subfield>
#<subfield code="i">INSPIRE-12245</subfield>
#<subfield code="u">Hamburg U., Inst. Theor. Phys. II</subfield>
# and returns Dappiaggi, Claudio [INSPIRE-12245] or just the name if no "i" present
	my $node = shift;
	my $name = $node->findvalue('./subfield[@code="a"]');
	my $id 	 = $node->findvalue('./subfield[@code="i"]');
	my $res  = $name . ($id ? " [".$id."]":"");
	return $res;
}
#----------------------------------------------------------------------
sub Fetch ($) {
	my ($identifier) = @_;
	my $url = "$prefix$identifier$suffix";

	my $ua = new LWP::UserAgent;
	$ua->agent("$useragent");
	$ua->env_proxy;

	my $request   = new HTTP::Request(GET,$url);
	my $response  = $ua->request($request);
	my $xmlresult = $response->content();

	my $xp        = XML::XPath->new(xml=>$xmlresult);
	my %record    = ();
	$record{SRC}        = "INSPIRE";
	$record{INSPIRE}    = $identifier;
	$record{title}      = $xp->findvalue('/collection/record/datafield[@tag="245"]')->string_value;
	$record{abstract}   = $xp->findvalue('/collection/record/datafield[@tag="520"]')->string_value;
	# these might be repeatable
	$record{doi}        = join(";",map(HGF::Forms::trim($_->string_value), 
					$xp->find('/collection/record/datafield[@tag="024"]/subfield[@code="a"]')->get_nodelist
				       )
				   );
	$record{repno}      = join(";",map(HGF::Forms::trim($_->string_value), 
					$xp->find('/collection/record/datafield[@tag="037"]/subfield[@code="a"]')->get_nodelist
				       )
				   );
	$record{vol}   = $xp->findvalue('//datafield[@tag="773"]/subfield[@code="v"]')->string_value;
	$record{issue}   = $xp->findvalue('/collection/record/datafield[@tag="773"]/subfield[@code="n"]')->string_value;	
	$record{year}   = $xp->findvalue('/collection/record/datafield[@tag="773"]/subfield[@code="y"]')->string_value;	
	$record{page}   = $xp->findvalue('/collection/record/datafield[@tag="773"]/subfield[@code="c"]')->string_value;	
	$record{comments}   = $xp->findvalue('/collection/record/datafield[@tag="500"]/subfield[@code="a"]')->string_value;
	$record{"AU"}	    = join(";",
			            ( 
			    	    map(HGF::Forms::trim(&AUString($_)), 
				        ($xp->find('/collection/record/datafield[@tag="100"]/subfield[@code="a"]/..')->get_nodelist,
					 $xp->find('/collection/record/datafield[@tag="700"]/subfield[@code="a"]/..')->get_nodelist)
				       )
				    )
				   ); # 100 + 700 are authors
	
	$record{created}    = $xp->findvalue('/collection/record/datafield[@tag="961"]/subfield[@code="x"]')->string_value;
	$record{updated}    = $xp->findvalue('/collection/record/datafield[@tag="961"]/subfield[@code="c"]')->string_value;
	# Strip linebreaks and normalize spaces
	$record{title}    =~ s/\n/ /g;
	$record{abstract} =~ s/\n/ /g;
	$record{title}    =~ s/\s{1,}/ /g;
	$record{abstract} =~ s/\s{1,}/ /g;
	$record{title}    = HGF::Forms::trim($record{title});
	$record{abstract} = HGF::Forms::trim($record{abstract});
	foreach my $key (keys(%record)) { # Clean up
		delete $record{$key} unless ($record{$key});
	};
	return(%record);
}



#use Data::Dumper;
#print Dumper(Fetch(858508));

1;

__END__

