# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2011, HGF
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""
Format journal reference properly
@author: arwagner
"""
__revision__ = "$Id$"

from invenio.bibformat_engine import BibFormatObject
from invenio.config import CFG_SITE_NAME

from invenio.config import \
     CFG_LINKRESOLVER, \
     CFG_LINKRESOLVERICON, \
     CFG_DOIRESOLVER

def format_element(bfo, separator='; ', highlight='yes'):
    """
    Format journal reference properly
    @param separator: the separator between urls.
    """

    """
    Markup:
    773 __ $a doi
    773 __ $y publication year
    773 __ $v volume
    773 __ $n issue
    773 __ $p page
    773 __ $t journal name 
    773 __ $x issn
    """

    id      = bfo.field("773__0")
    doi     = bfo.field("773__a")
    py      = bfo.field("773__y")
    vol     = bfo.field("773__v")
    issue   = bfo.field("773__n")
    page    = bfo.field("773__p")
    journal = bfo.field("773__t")
    issn    = bfo.field("773__x")

    refs = []
    ref = ''
    if id != '':
      if highlight == 'yes':
        ref += '<a href="/search?cc=Periodicals&p1='
        ref += id
        ref += '">'
    if journal != '':
      if highlight == 'yes':
         ref += ' <span class="refjournal">'
      ref += journal
      if highlight == 'yes':
         ref += '</span></a>'
      else:
         ref += ' '
    if vol != '':
      if highlight == 'yes':
         ref += ' <span class="refvolume">'
      ref += vol
      if highlight == 'yes':
         ref += '</span>'
      else:
         ref += ' '
    if issue != '':
      if highlight == 'yes':
         ref += ' <span class="refissue">'
      ref += issue
      if highlight == 'yes':
         ref += '</span>'
      else:
         ref += ' '
    if py != '':
      if highlight == 'yes':
         ref += ' <span class="refyear">' 
      ref += '(' + py + ')'
      if highlight == 'yes':
         ref += '</span>'
      else:
         ref += ' '
    if page != '':
      if highlight == 'yes':
         ref += ' <span class="refpage">'
      ref += page
      if highlight == 'yes':
         ref += '</span>'
      else:
         ref += ' '
    if doi != '':
      if highlight == 'yes':
        ref += ' <span class="refdoi"><a href="' + CFG_DOIRESOLVER + doi + '">'
        ref += '[' + doi +  ']'
        ref += '</a></span>'
      else:
         ref += '\n' + 'http://dx.doi.org/' + doi + '\n'
         ref += doi
         ref += ' '

    # Only construct a string if we have a reference, otherwise it
    # will trigger the prefix to display.
    if ref != '':
      if highlight == 'yes':
        ref = '<span class="journalref">' + ref + '</span>'
      refs.append(ref)

    return separator.join(refs)

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0

def test_format(recID, hl):
    """
    only for testing of format
    """
    bfo = BibFormatObject(recID)
    print format_element(bfo, highlight=hl)
 
if __name__ == '__main__': 
    #test_format(recID = 130114, hl='no')
    test_format(recID = 130425, hl='no')
