package PICA::PSI::XML;

=head1 NAME

PICA::PSI::HTML - experimental API to XML interface of PSI

=head1 SYNOPSIS

=cut

use strict;


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

1;

__END__
