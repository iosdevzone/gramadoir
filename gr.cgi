#!/usr/bin/perl -wT
#  Under gentoo's apache configuration, this goes in /home/httpd/cgi-bin
#  owner and group are "apache".

use strict;
use CGI;
use Lingua::GA::Gramadoir;
use Lingua::GA::Gramadoir::Languages;

my $VERSION = '0.61';

my $lh;

sub gettext
{
	my ( $string, @rest ) = @_;

	$string =~ s/\\n/\n/g;
	$string =~ s/\%s/[_1]/;
	return $lh->maketext($string, @rest);
}

binmode STDOUT, ":utf8";

$CGI::DISABLE_UPLOADS = 1;
$CGI::POST_MAX        = 1024;

$ENV{PATH}="/bin:/usr/bin";
delete @ENV{ 'IFS', 'CDPATH', 'ENV', 'BASH_ENV' };

my $q = new CGI;
# /^(['����������\w\s,.!?-]+)$/ is better
my $pure_input = $q->param( "foirm_ionchur" );
my $ionchur;
my $pure_lang = $q->param( "teanga" );
my $teanga;

( $ionchur ) = $pure_input =~ /^(.+)$/s if defined $pure_input;
( $teanga ) = $pure_lang =~ /^([a-z][a-z](?:_[A-Z][A-Z])?)$/ if defined $pure_lang;

if (defined $teanga) {
	$lh = Lingua::GA::Gramadoir::Languages->get_handle($teanga);
}
else {
	$lh = Lingua::GA::Gramadoir::Languages->get_handle();
}
die "Problem setting language handle" unless $lh;

# rightfully this file should go in po/POTFILES.in
# but each string is taken directly from gram.pl
my $clar = gettext('An Gramadoir');
my $vstring = gettext('version %s', $VERSION);
my $copyright = 'Copyright (C) 2003-2007 <a href="http://borel.slu.edu/">Kevin P. Scannell</a><br><br>';
my $gpl = gettext('This is free software; see the source for copying conditions.  There is NO\\nwarranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE,\\nto the extent permitted by law.');

print $q->header(-type=>"text/html",
		 -charset=>'utf-8'),
"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01//EN\"\n",
"\"http://www.w3.org/TR/html4/strict.dtd\">\n",
"<html>\n",
"<head>\n",
"<title>An Gramad&oacute;ir</title>\n",
"<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\">\n",
"<link rel=\"stylesheet\" href=\"http://borel.slu.edu/kps.css\" type=\"text/css\">\n",
"</head>\n<body>\n";

print "<p>\n<a href=\"http://borel.slu.edu/gramadoir/\">$clar</a>, $vstring<br>\n$copyright\n<i>$gpl</i></p><hr>\n";

if (defined($ionchur)) {
	my $gr = new Lingua::GA::Gramadoir(
		fix_spelling => 1,
		interface_language => $teanga,
	);

	foreach (@{$gr->grammatical_errors($ionchur)}) {
		(my $ln, my $snt, my $msg) = m/^<error fromy="([0-9]+)".* context="(.*)" msg="([^"]+)"\/>$/;
		$snt =~ s/<marker>/<b class=gramadoir>/;
		$snt =~ s/<\/marker>/<\/b>/;
		print "<br><br>$ln: $snt<br>\n$msg.\n\n";
	}
}
else {
	$ionchur = '<<empty input>>';
}

$teanga = '<<no language>>' unless defined $teanga;

print $q->hr;
print $q->end_html;

# remainder writes to log file
my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime time;
my $datestr = sprintf("%04d-%02d-%02d", $year+1900, $mon+1, $mday);
open (LOGFILE, '>>/home/httpd/gr.log') or die "Could not open log file: $!\n";
print LOGFILE "$datestr\nTeanga=$teanga\n$ionchur\n\n";

exit 0;
