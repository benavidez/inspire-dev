package PICA::XMLWriter;

=head1 NAME

PICA::XMLWriter - Write and count PICA+ records and fields in XML format

=cut

use strict;
use warnings;

use PICA::Writer;
use Carp;

use base qw( PICA::Writer );
our $VERSION = "0.43";
our $NAMESPACE = 'info:srw/schema/5/picaXML-v1.0';

=head1 METHODS

=head2 new ( [ <file-or-handle> ] [, %parameters ] )

Create a new XML writer.

=cut

sub new {
    my $class = shift;
    my ($fh, %params) = @_ % 2 ? @_ : (undef, @_);
    my $self = bless { }, $class;
    return $self->reset($fh);
}

=head2 write ( [ $comment, ] $record [, $record ... ] )

Write a record(s) of type L<PICA::Record>. You can also pass
strings that will be printed as comments. Please make sure to
have set the default namespace ('info:srw/schema/5/picaXML-v1.0')
to get valid PICA XML.

=cut

sub write {
    my $self = shift;

    my $comment = "";
    while (@_) {
        my $record = shift;

        if (ref($record) eq 'PICA::Record') {
            if ( $self->{filehandle} ) {
                $self->start_document() unless $self->{in_doc};
                print { $self->{filehandle} } $record->to_xml() ;
            }
            $comment = "";

            $self->{recordcounter}++;
            $self->{fieldcounter} += scalar $record->all_fields;
        } elsif (ref(\$record) eq 'SCALAR') {
            next if !$record;
            $comment .= "\n" if $comment;
            $comment .= '# ' . join("\n# ", split(/\n/,$record)) . "\n";
            $comment =~ s/--//g;
            print "<!-- $comment -->";
        } else {
            croak("Cannot write object of unknown type (PICA::Record expected)!");
        }
    }
}

=head2 writefield ( $field [, $field ... ] )

Write one ore more C<PICA::Field> in XML, based on C<PICA::Field->to_xml>.

=cut

sub writefield {
    my $self = shift;
    while (@_) {
        my $field = shift;
        if (ref($field) ne 'PICA::Field') {
            croak("Cannot write object of unknown type (PICA::Field expected)!");
        } else {
            print { $self->{filehandle} } $field->to_xml() if $self->{filehandle};
            $self->{fieldcounter}++;
        }
    }
}

=head2 start_document

Write XML header and collection start element. 
The default namespace is set to 'info:srw/schema/5/picaXML-v1.0'.

=cut

sub start_document {
    my $self = shift;
    if ($self->{filehandle}) {
        print { $self->{filehandle} } "<?xml version='1.0' encoding='UTF-8'?>\n";
        print { $self->{filehandle} } "<collection xmlns='" . $NAMESPACE . "'>\n";
    }
    $self->{in_doc} = 1;
}

=head2 end_document

Write XML footer (collection end element).

=cut

sub end_document {
    my $self = shift;
    print { $self->{filehandle} } "</collection>\n" if $self->{filehandle} and $self->{in_doc};
    $self->{in_doc} = 0;
}

1;

__END__

=head1 AUTHOR

Jakob Voss C<< <jakob.voss@gbv.de> >>

=head1 LICENSE

Copyright (C) 2007, 2008 by Verbundzentrale Goettingen (VZG) and Jakob Voss

This library is free software; you can redistribute it and/or modify it
under the same terms as Perl itself, either Perl version 5.8.8 or, at
your option, any later version of Perl 5 you may have available.

