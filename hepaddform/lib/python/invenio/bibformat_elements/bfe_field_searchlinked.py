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
BibFormat element - Prints field with search link
local element by Forschungszentrum Juelich
@author: arwagner
"""
__revision__ = "$Id$"

from urllib import quote, quote_plus

from invenio.config import CFG_SITE_URL

from invenio.bibformat_engine import BibFormatObject


def format(bfo, tag, index ,style="", separator='; '):
    """
    This is the default format for fields with search links
    @param separator: the separator between fields
    @param style: CSS class of the link
    """
    
    results = bfo.fields(tag)
    
    if style != "":
        style = 'class="'+style+'"'

    urls = ['<a '+ style + \
            'href="' + CFG_SITE_URL + \
                        '/search?f='+index+'&amp;p='+quote_plus(result)+ \
                          '&amp;ln='+bfo.lang+ \
                          '">'+result+'</a>'                
            for result in results]
        
    return separator.join(urls)
          

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0

def test_format(recID, tag, index):
    """
    only for testing of format
    """
    bfo = BibFormatObject(recID)
    print format(bfo, tag, index)
 
if __name__ == '__main__': 
    test_format(recID = 149683, tag='920__v', index='institute' )
    test_format(recID = 149683, tag='500__3', index='littype' )
