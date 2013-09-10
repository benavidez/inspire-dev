# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2011, HGF
##
## CDS Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## CDS Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with CDS Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""
BibFormat element - realise horizontal and vertical linking in
authority records
@author: arwagner
"""
__revision__ = "$Id$"

from invenio.bibformat_engine import BibFormatObject
from invenio.urlutils import create_html_link
from invenio.config import CFG_SITE_URL

from invenio.search_engine import \
  perform_request_search


def format(bfo, tag='510__', display='a', link='w', id='0', separator='&nbsp;&nbsp;&nbsp;'):
    """
    Generate horzontal and vertical linking for authority records.
    Linkage is usually done by assigning letters to $w
    (http://www.loc.gov/marc/authority/adtracing.html):
    a : earlier form
    b : later form
    t : immediate top
    """

    #display = bfo.fields(tag+display)
    #idval   = bfo.fields(tag+id)
    #link    = bfo.fields(tag+link)

    tag     = bfo.fields(tag)
    result = []

    baseurl = CFG_SITE_URL + '/search?ln='+ bfo.lang + '&p='

    earlier = [] 
    later   = []
    top     = []

    for field in tag:
      url = baseurl + '035__a:' + field[id]
      recid = perform_request_search(p='035__a:' + field[id])
      try:
        url = CFG_SITE_URL + '/record/' + str(recid[0])
      except: 
        url = ''
      if link in field:
         if field[link] == 'a':
            if url != '':
               text = '<font size="+3">⇦</font> ' + field[display]
               earlier.append(create_html_link(url, {}, link_label=text, linkattrd={}))
         if field[link] == 'b':
            if url != '':
               text = field[display] + ' <font size="+3">⇨</font>'
               later.append(create_html_link(url, {}, link_label=text, linkattrd={}))
         if field[link] == 't':
            if url != '':
               text = '<font size="+3">⇧</font> '     + field[display] + ' <font size="+3">⇧</font>'
               top.append(create_html_link(url, {}, link_label=text, linkattrd={}))
      

    result += earlier
    result += top
    result += later

    return separator.join(result)
            

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0

def test_format(recID, tag='510__', display='a', link='w', id='0', separator='&nbsp;&nbsp;&nbsp;'):
    """
    only for testing of format
    """
    bfo = BibFormatObject(recID)
    print format(bfo, tag, display, link, id, separator)
 

if __name__ == '__main__': 
    test_format(recID = 2574)
    test_format(recID = 130424, tag='550__')
