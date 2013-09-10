package MarcXML;
#=========================================================================
#
#    MarcXML.pm
#
#    Simple routines to output MarcXML tags.
#
#    $Id: $
#    Last change: <Mo, 2011/10/24 12:51:38  ZB0063>
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


use IO::Handle;
use Encode;

*STDOUT->autoflush(1);    # Unbuffered screen IO

@ISA    = ('Exporter');
@EXPORT = qw();

#======================================================================

=head1 NAME

Write MARC XML fields

=cut
#----------------------------------------------------------------------

#----------------------------------------------------------------------
=head2 fun

what it does

	$res     : XML result from query

Status: checked

=cut
#----------------------------------------------------------------------
#
sub xmlesc($) {
	 my ($xml) = @_;
	 if ((defined($xml)) and ($xml ne "")) {
			$xml =~ s/\&/\&amp;/g;
			$xml =~ s/\&amp;amp;/\&amp;/g;
			$xml =~ s/</\&lt;/g;
			$xml =~ s/>/\&gt;/g;
			$xml =~ s/"/\&quot;/g;
			$xml =~ s/'/\&apos;/g;
			return($xml);
	 } else {
			return("");
	 }

}

sub GetMarcControlfield($$){
	my ($tag, $value) = @_;

	$value = xmlesc($value);
	my $str = "<controlfield tag=\"$tag\">$value</controlfield>\n";
	return($str);

}

sub MarcField($$$%) {
	 my ($tag, $ind1, $ind2, %subfields) = @_;

	 # According to Marc a field may only be issued if  it has at least
	 # one subfield. No empty subfields are allowed either.
	 my $nofield = 1;
	 for my $subfield ( sort keys %subfields) {
		 my $value = xmlesc($subfields{$subfield});
		 $nofield = 0 if (defined($value) and $value ne "");
	 }

	 my $str = "";
	 if ($nofield < 1) {
			$str  = "  <datafield tag=\"$tag\" ind1=\"$ind1\" ind2=\"$ind2\">\n";
			for my $subfield ( sort keys %subfields) {
				my $value = xmlesc($subfields{$subfield});
				if ($value ne "") {
					 $str .= "     <subfield code=\"$subfield\">$value</subfield>\n";
				}
			}
			$str .= "  </datafield>\n";
	 }
	 return($str);
}

sub GetMarc($$$$$) {
	my ($tag, $ind1, $ind2, $subfield, $value) = @_;
	return("") if ((not(defined($value))) or $value eq "");

	$value = xmlesc($value);
	$str  = "  <datafield tag=\"$tag\" ind1=\"$ind1\" ind2=\"$ind2\">\n";
	$str .= "     <subfield code=\"$subfield\">$value</subfield>\n";
	$str .= "  </datafield>\n";
	return($str);
}

sub GetMarcDatafield($$$) {
	my ($tag, $ind1, $ind2) = @_;
	return("  <datafield tag=\"$tag\" ind1=\"$ind1\" ind2=\"$ind2\">\n");
}
	
	
sub GetMarcSubfield($$) {
	my ($subfield, $value) = @_;
	$value = xmlesc($value);
	return("") if $value eq "";
	return("     <subfield code=\"$subfield\">$value</subfield>\n");
}
sub EndMarcDatafield() {
	return("  </datafield>\n");
}

1;

__END__

