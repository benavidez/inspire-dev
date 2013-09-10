package PICA::PSI::HTML;

=head1 NAME

PICA::PSI::HTML - experimental API to HTML interface of PSI

=head1 SYNOPSIS

=cut

use strict;

use PICA::Field;
use PICA::Record;

use Carp;

use LWP::UserAgent;
use URI::Escape;

=head1 METHODS

=head2 new()
=cut

sub new {
    my $class = shift;
    $class = ref($class) || $class;
    my $baseurl = shift;
    my $log = shift;

    my $self = bless {
        _baseurl => $baseurl,
        _log => $log
    }, $class;

    return $self;
}

=head2 log()
=cut

sub log {
    my $self = shift;
    my $msg = shift;
    my $log = $self->{_log};

    $log->($msg) if $log;
}

=head2 fetchPPN()

fetch a record by PPN

=cut

sub fetchPPN {
    my $self = shift;
    my $ppn = shift;

    my $url = $self->{_baseurl} . "PRS=PP/PPN?PPN=$ppn";

    $self->log("fetching $url");;

    my $ua = LWP::UserAgent->new();
    my $res = $ua->get( $url );
    my $html = $res->decoded_content();

    my $record = $self->parse_html( $html );

    return $record;
}

=head2 fetchIKT()

get the first matching record

=cut

sub fetchIKT {
    my ($self, $ikt, $trm) = @_;

    my $url = $self->{_baseurl} . "CMD?ACT=SRCHA&IKT=$ikt&TRM=$trm&PRS=PP";

    $self->log("fetching $url");;

    my $ua = LWP::UserAgent->new();
    my $res = $ua->get( $url );
    my $html = $res->decoded_content();

    my $record = $self->parse_html( $html );

    return $record;
}

=head2 fetchIKTMat()

get the first matching record

=cut

sub fetchIKTMat {
    my ($self, $ikt, $trm, $mat) = @_;

    my $url = $self->{_baseurl} . 'IMPLAND=Y/CMD?ACT=SRCHM&PRS=PP&MATCFILTER=Y&MATCSET=Y&ACT0=SRCH&IKT0=' .
$ikt . '&TRM0=' . uri_escape($trm) . '&ADI_MAT=' . $mat;

    $self->log("fetching $url");;

    my $ua = LWP::UserAgent->new();
    my $res = $ua->get( $url );
    my $html = $res->decoded_content();

    my $record = $self->parse_html( $html );

    return $record;
}

use XML::Simple;

=head2 fetchPPNListByXML

get list of PPN

=cut

sub fetchPPNListByXML {
    my ($self, $act) = @_;

    my $url = $self->{_baseurl} . "XML=1.0/IMPLAND=Y/CMD?ACT=" . $act;

    $self->log("fetching with XML $url");;

    my $ua = LWP::UserAgent->new();
    my $res = $ua->get( $url );
    my $xml = $res->decoded_content();
    return if !$xml;

    #my $record = $self->parse_html( $html );
  my $resulthits = 0;
  my @resultPPNs;

  require XML::Parser;
  my $parser = new XML::Parser(
     Handlers => { Start => sub {
        my ($p, $tag, %attr) = @_;
        if ($tag eq "SHORTTITLE") {
            push (@resultPPNs, $attr{PPN}) if defined $attr{PPN};
        } elsif ($tag eq "SET") {
            $resulthits = $attr{hits} if defined $attr{hits};
        }
     } }
  );

  $parser->parse($xml);

  return @resultPPNs;
}

=head2 parse_html (html)

Parse HTML data and extract a PICA+ record. Returns a L<PICA::Record> 
or undef if no PICA+ data could be found. May throw an error on invalid
PICA+ data.

=cut

sub parse_html {
    my ($self, $html) = @_;

    my @lines = split(/\n/, $html);

    my $record = PICA::Record->new();

    foreach my $line (@lines) {
        if ($line =~ /<TR><TD>([0-9][0-9][0-9][0-9A-Z@]([\/][0-9][0-9])?)<\/TD><TD>([^<]*)<\/TD><\/TR>/) {
            my ($tag, $value) = ($1, $3);

            # TODO: There may be more entities (&lt; etc.)
            $value =~ s/&lt;/</g;
            $value =~ s/&gt;/>/g;
            $value =~ s/&amp;/&/g;

            $value =~ s/\$/\x1F/g; # subfield indicator

            my $field = PICA::Field->parse($tag." ". $value);
            $record->append($field) if $field;
        }
    }

	 # return if $record->is_empty();
    return $record;
}

1;

__END__
