package PICA::SRUSearchParser;

=head1 NAME

PICA::SRUSearchParser - Parse a SRU response in XML and extract PICA+ records.

=cut

use strict;

our $VERSION = "0.48";

=head1 SYNOPSIS

    $parser = PICA::SRUSearchParser->new();
    $xmlparser = $parser->parse( $sru );

    print "numberOfRecords: " . $parser->numberOfRecords . "\n";
    print "resultSetId: " . $parser->resultSetId . "\n";
    print "result: " . $xmlparser->counter() . "\n";

=cut

use Carp qw(croak);
use PICA::XMLParser;
use XML::Parser;

=head1 METHODS

=head2 new ( [ $xmlparser ] )

Creates a new XML parser to parse an SRU Search Response document.
PICA Records are passed to a L<PICA::XMLParser> that must be provided.

=cut

sub new {
    my ($class, $xmlparser) = @_;
    $class = ref $class || $class;

    $xmlparser = PICA::XMLParser->new()
        unless UNIVERSAL::isa($xmlparser, "PICA::XMLParser");

    my $self = {
        xmlparser => $xmlparser,
        char_data => "",
        in_record => 0,
        numberOfRecords => undef,
        currentNumber => 0,
        resultSetId => undef,
    };

    return bless $self, $class;
}

=head2 parse( $document )

Parse an SRU SearchRetrieve Response (given as XML document)
and return the L<PICA::XMLParser> object that has been used.

=cut

sub parse {
    my ($self, $document) = @_;
    my $sruparser = XML::Parser->new(
       Handlers => {    # TODO: memory leak (?)
          Start => sub {$self->StartTag(@_)},
          End   => sub {$self->EndTag(@_)},
          Char  => sub {$self->Text(@_)}
#         # TODO: Init and Final are never called. Do we need them?
       }
    );
    $self->{currentNumber} = 0;
    $sruparser->parse($document);
    return $self->{xmlparser};
}

=head2 numberOfRecords ()

Get the total number of records in the SRU result set.
The result set may be split into several chunks.

=cut

sub numberOfRecords {
    my $self = shift;
    return $self->{numberOfRecords};
}

=head2 currentNumber ()

Get the current number of records that has been passed.
This is equal to or less then numberOfRecords.

=cut

sub currentNumber {
    my $self = shift;
    return $self->{currentNumber};
}

=head2 resultSetId ()

Get the SRU resultSetId that has been parsed.

=cut

sub resultSetId {
    my $self = shift;
    return $self->{resultSetId};
}

=head1 PRIVATE HANDLERS

This methods are private SAX handlers to parse the XML.

=head2 StartTag

SAX handler for XML start tag. On PICA+ records this calls 
the start handler of L<PICA::XMLParser>, outside of records
it parses the SRU response.

=cut

sub StartTag {
    my ($self, $parser, $name, %attrs) = @_;
    if ($self->{in_record}) {
        $self->{xmlparser}->start_handler($parser, $name, %attrs);
    } else {
        $self->{char_data} = "";
        if ($name eq "srw:recordData") {
            $self->{in_record} = 1;
        }
    }
}

=head2 EndTag

SAX handler for XML end tag. On PICA+ records this calls 
the end handler of L<PICA::XMLParser>.

=cut

sub EndTag {
    my ($self, $parser, $name) = @_;

    if ($self->{in_record}) {
        if ($name eq "srw:recordData") {
            $self->{currentNumber}++;
            $self->{in_record} = 0;
        } else {
            $self->{xmlparser}->end_handler($parser, $name);
        }
    } else {
        if ($name eq "srw:numberOfRecords") {
            $self->{numberOfRecords} = $self->{char_data};
        } elsif ($name eq "srw:resultSetId") {
            $self->{resultSetId} = $self->{char_data};
        }
    }
}

=head2 Text

SAX handler for XML character data. On PICA+ records this calls 
the character data handler of L<PICA::XMLParser>.

=cut

sub Text {
    my ($self, $parser, $string) = @_;

    if ($self->{in_record}) {
        $self->{xmlparser}->char_handler($parser, $string);
    } else {
        $self->{char_data} .= $string;
    }
}

1;

=head1 AUTHOR

Jakob Voss C<< <jakob.voss@gbv.de> >>

=head1 LICENSE

Copyright (C) 2007-2009 by Verbundzentrale Goettingen (VZG) and Jakob Voss

This library is free software; you can redistribute it and/or modify it
under the same terms as Perl itself, either Perl version 5.8.8 or, at
your option, any later version of Perl 5 you may have available.
