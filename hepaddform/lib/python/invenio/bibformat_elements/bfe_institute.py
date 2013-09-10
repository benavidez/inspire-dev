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
BibFormat element - Print the institute from field 9201_ and make a
link by it's ID number.
@author: arwagner
"""
__revision__ = "$Id$"

from invenio.bibformat_engine import BibFormatObject
from invenio.urlutils import create_html_link
from invenio.config import CFG_SITE_URL


def format(bfo, separator='; '):
    """
    This is the default format for institutional infos.
    @param separator: the separator between FuEs
    """

    sub_insts       = bfo.fields("9201_l")
    sub_insts_short = bfo.fields("9201_k")
    sub_insts_id    = bfo.fields("9201_0")
    result = []

    # All contributing institutes
    M9201 = bfo.fields("9201_")

    # assemble all data from 913 and 536
    insthash = {}
    instsortedarray = []
    x = 0
    for i in M9201:
      inst          = {}
      try:
         id            = i['0']
      except:
        id = ''
      inst['id']    = id
      try:
        inst['title'] = i['l']
      except:
        inst['title'] = ''
      try:
        inst['short'] = i['k']
      except:
        inst['short'] = ''
      try:
        inst['order'] = i['x']
      except:
        inst['order'] = x
      insthash[id]  = inst
      # we need to initialise the array as empty to fill it in in
      # sorted order later on.
      instsortedarray.append('')
      x += 1

    for id in insthash:
      inst = insthash[id]
      index = insthash[id]['order']
      print index
      print inst
      instsortedarray[int(index)] = inst

    baseurl = CFG_SITE_URL + '/search?ln='+ bfo.lang + '&p='
    result = []
    result.append('<ol>')
    for inst in instsortedarray:
      id = inst['id']
      ti = inst['title']
      sh = inst['short']
      title = ti
      if sh != '':
         title = title + ' (' + sh + ')'
      url = CFG_SITE_URL + '/search?cc=Institutes&p='+id+ '&action_search=Search'
      link = create_html_link(url, {}, link_label=title, linkattrd={})
      result.append('<li>' + link + '</li>')
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
    print format(bfo)
 
if __name__ == '__main__': 
    test_format(recID = 100882)
