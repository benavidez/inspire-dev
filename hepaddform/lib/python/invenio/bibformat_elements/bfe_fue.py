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
BibFormat element - Prints FuE infos.
local element by Forschungszentrum Juelich
@author: arwagner
"""
__revision__ = "$Id$"

from invenio.bibformat_engine import BibFormatObject
from urllib import quote, quote_plus
from invenio.config import CFG_SITE_URL
from invenio.urlutils import create_html_link


def format_element(bfo, separator='; '):
    """
    This is the default format for FuE infos.
    @param separator: the separator between FuEs
    """
    
    FuEID      = bfo.fields("9131_0")
    FuEs       = bfo.fields("9131_v")
    FuEs_short = bfo.fields("9131_k")
    result = []

    # All grants
    M536 = bfo.fields("536__")
    # All HGF specific addenda
    M913 = bfo.fields("9131_")

    # assemble all data from 913 and 536
    granthash = {}

    grantsortedarray = []
    i = 0
    for g in M536:
      grant = {}
      try:
        id    = g['0']
      except:
        # we need an id, as we want to sort together
        id    = i

      grant['id']     = id
      try:
         grant['title']  = g['a']
      except:
         grant['title']  = ''
      try:
         grant['order']  = g['x']
      except:
         grant['order']  = i
      try:
         grant['number'] = g['c']
      except:
        pass
      try:
         grant['call']   = g['f']
      except:
        pass
      granthash[id] = grant
      # we need to initialise the array as empty to fill it in in
      # sorted order later on.
      grantsortedarray.append('')
      i += 1

    i = 0
    for g in M913:
      id    = g['0']
      try:
        id    = g['0']
      except:
        # we need an id, as we want to sort together
        id    = i
      grant = granthash[id]
      try:
         grant['schwerpunkt'] = g['b']
      except:
        pass
      try:
         grant['kuerzel']     = g['k']
      except:
        pass
      try:
         grant['programm']    = g['l']
      except:
        pass
      try:
         grant['vorhaben']    = g['v'] # == lafa
      except:
        pass
      try:
         grant['vk']          = g['u'] # == lafa kürzel = vorhabenkürzel
      except:
        pass
      granthash[id] = grant
      i += 1

      for id in granthash:
        grant = granthash[id]
        index = granthash[id]['order']
        grantsortedarray[int(index)] = grant


      result = []
      result.append('<ol>')
      for grant in grantsortedarray:
        id = grant['id']
        ti = grant['title']
        fue= '';
        try:
          fue= '(' + grant['schwerpunkt'] + ')'
        except:
          pass
        url = CFG_SITE_URL + '/search?cc=Grants&p='+id+ '&action_search=Search'
        link = create_html_link(url, {}, link_label=ti, linkattrd={})
        result.append('<li>' + link + " " + fue + '</li>')
      result.append('</ol>')

      return separator.join(result)

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0

def test_format(recID):
    """
    only for testing of format
    """
    bfo = BibFormatObject(recID)
    print format_element(bfo)
 
if __name__ == '__main__': 
    test_format(recID = 130122)
