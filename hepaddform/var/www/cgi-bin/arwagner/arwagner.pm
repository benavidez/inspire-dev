package arwagner;
#=========================================================================
#
#    arwagner.pm
#
#    Some tools
#
#    $Id: $
#    Last change: <Mo, 2011/04/11 15:58:24  ZB0063>
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

#======================================================================

=head1 NAME

#----------------------------------------------------------------------
=head2 trim

Remove blacks from a string

Status: checked

=cut
#----------------------------------------------------------------------
sub trim {
	my @text = @_;
	for (@text) {
		if (defined($_))  {
			 s/^\s+//g;
			 s/\s+$//;
		}
	}
	return wantarray ? @text : $text[0];
}

#----------------------------------------------------------------------
=head2 strip

Remove non-ASCII chars
see: http://www.perlmonks.org/?node_id=613773

Status: checked

=cut
#----------------------------------------------------------------------
sub strip {
  my $s =  shift;
  $s    =~ s/[^[:ascii:]]+//g;
  return $s;
}

#----------------------------------------------------------------------
=head2 AddSQLString

Quote the string and add the separator

$value    : The value to be quoted for SQL
$separator: The separator, e.g. ", " or ");"

Status: checked

=cut
#----------------------------------------------------------------------
sub AddSQLString($$) {
	my ($value, $separator) = @_;

	if (defined($value)) {
		# $value =~ s/"/""/g;
		$value =~ s/'/''/g;
		return "\'$value\'$separator";
	}
	else {
		return "\'\'$separator";
	}
}

#----------------------------------------------------------------------
=head2 ExtractCSVHeader

Read the heading line of a CSV file and return a hash with column association

Status: checked

=cut
#----------------------------------------------------------------------
sub ExtractCSVHeader($$) {
	my ($FH, $delimiter) = @_;
	
	my $headln = $FH;
	$headln =~ s/\n//;
	my @headings = split(/$delimiter/, $headln);
	my %cols = ();
	for (my $i=0; $i <= $#headings; $i++) {
		$cols{lc($headings[$i])} = $i
	}
	return %cols;
}

# http://rami.info/2005/11/19/urlencode-and-urldecode-for-perl/
sub URLDecode {
	 my $theURL = $_[0];
	 $theURL =~ tr/+/ /;
	 $theURL =~ s/%([a-fA-F0-9]{2,2})/chr(hex($1))/eg;
	 $theURL =~ s/<!–(.|\n)*–>//g;
	 return $theURL;
}

sub URLEncode {
	 my $theURL = $_[0];
	 $theURL =~ s/([\W])/"%" . uc(sprintf("%2.2x",ord($1)))/eg;
	 return $theURL;
}


1;

__END__

