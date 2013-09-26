#!/usr/bin/perl

=pod

=cut

=head1

Install the perl module dependencies for the journal submission form
based on HGF

=cut

use strict;
use warnings;

use CPAN;
use File::Path qw(make_path remove_tree);

CPAN::HandleConfig->load;
CPAN::Shell::setup_output;
make_path($CPAN::Config->{cpan_home}.'/Bundle/Forms');
open my $BUNDLE, '>',
$CPAN::Config->{cpan_home}.'/Bundle/Forms/HGF.pm' or die "couldn't
create bundle file: $!";
while (<DATA>) {
      print ${BUNDLE} $_;
}
close $BUNDLE or warn "problem closing file: $!";

CPAN::Shell->install("Bundle::Forms::HGF");

# remove_tree($CPAN::Config->{cpan_home});

 __DATA__

package Bundle::Forms::HGF

$VERSION = '0.01';

1;

__END__

=head1 NAME

Bundle::Forms::HGF - Perl dependencies for HGF forms

=head1 SYNOPSIS

perl -MCPAN -e 'install Bundle::Forms::HGF'

=head1 CONTENTS

Config::Simple 4.58

DBD::SQLite 1.40

JSON 2.59

LWP::Protocol::https 6.04

SOAP::Lite 1.06

String::Escape 2010.002

XML::XPath 1.13

YAML 0.84

CGI 3.63

IO::Scalar 2.110

Term::ReadKey 2.30


=head1 CONFIGURATION

Summary of my perl5 (revision 5 version 10 subversion 1) configuration:
   
  Platform:
    osname=linux, osvers=2.6.32-220.el6.x86_64, archname=i386-linux-thread-multi
    uname='linux c6b7.bsys.dev.centos.org 2.6.32-220.el6.x86_64 #1 smp tue dec 6 19:48:22 gmt 2011 i686 i686 i386 gnulinux '
    config_args='-des -Doptimize=-O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector --param=ssp-buffer-size=4 -m32 -march=i686 -mtune=atom -fasynchronous-unwind-tables -DDEBUGGING=-g -Dversion=5.10.1 -Dmyhostname=localhost -Dperladmin=root@localhost -Dcc=gcc -Dcf_by=Red Hat, Inc. -Dprefix=/usr -Dvendorprefix=/usr -Dsiteprefix=/usr/local -Dsitelib=/usr/local/share/perl5 -Dsitearch=/usr/local/lib/perl5 -Dprivlib=/usr/share/perl5 -Darchlib=/usr/lib/perl5 -Dvendorlib=/usr/share/perl5/vendor_perl -Dvendorarch=/usr/lib/perl5/vendor_perl -Dinc_version_list=5.10.0 -Darchname=i386-linux-thread-multi -Duseshrplib -Dusethreads -Duseithreads -Duselargefiles -Dd_dosuid -Dd_semctl_semun -Di_db -Ui_ndbm -Di_gdbm -Di_shadow -Di_syslog -Dman3ext=3pm -Duseperlio -Dinstallusrbinperl=n -Ubincompat5005 -Uversiononly -Dpager=/usr/bin/less -isr -Dd_gethostent_r_proto -Ud_endhostent_r_proto -Ud_sethostent_r_proto -Ud_endprotoent_r_proto -Ud_setprotoent_r_proto -Ud_endservent_r_proto -Ud_setservent_r_proto -Dscriptdir=/usr/bin -Dusesitecustomize'
    hint=recommended, useposix=true, d_sigaction=define
    useithreads=define, usemultiplicity=define
    useperlio=define, d_sfio=undef, uselargefiles=define, usesocks=undef
    use64bitint=undef, use64bitall=undef, uselongdouble=undef
    usemymalloc=n, bincompat5005=undef
  Compiler:
    cc='gcc', ccflags ='-D_REENTRANT -D_GNU_SOURCE -fno-strict-aliasing -pipe -fstack-protector -I/usr/local/include -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64',
    optimize='-O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector --param=ssp-buffer-size=4 -m32 -march=i686 -mtune=atom -fasynchronous-unwind-tables',
    cppflags='-D_REENTRANT -D_GNU_SOURCE -fno-strict-aliasing -pipe -fstack-protector -I/usr/local/include'
    ccversion='', gccversion='4.4.6 20120305 (Red Hat 4.4.6-4)', gccosandvers=''
    intsize=4, longsize=4, ptrsize=4, doublesize=8, byteorder=1234
    d_longlong=define, longlongsize=8, d_longdbl=define, longdblsize=12
    ivtype='long', ivsize=4, nvtype='double', nvsize=8, Off_t='off_t', lseeksize=8
    alignbytes=4, prototype=define
  Linker and Libraries:
    ld='gcc', ldflags =' -fstack-protector -L/usr/local/lib'
    libpth=/usr/local/lib /lib /usr/lib
    libs=-lresolv -lnsl -lgdbm -ldb -ldl -lm -lcrypt -lutil -lpthread -lc
    perllibs=-lresolv -lnsl -ldl -lm -lcrypt -lutil -lpthread -lc
    libc=/lib/libc-2.12.so, so=so, useshrplib=true, libperl=libperl.so
    gnulibc_version='2.12'
  Dynamic Linking:
    dlsrc=dl_dlopen.xs, dlext=so, d_dlsymun=undef, ccdlflags='-Wl,-E -Wl,-rpath,/usr/lib/perl5/CORE'
    cccdlflags='-fPIC', lddlflags='-shared -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector --param=ssp-buffer-size=4 -m32 -march=i686 -mtune=atom -fasynchronous-unwind-tables -L/usr/local/lib'



=head1 AUTHOR

 =cut


