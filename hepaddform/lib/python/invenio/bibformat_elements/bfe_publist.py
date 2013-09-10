# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2012, HGF
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
Use the ID number in 035__a to fetch a list of pulications associated
with this ID
@author: arwagner
"""
__revision__ = "$Id$"

from invenio.bibformat_engine import BibFormatObject
from invenio.search_engine import \
  perform_request_search, \
  print_record, \
  print_records

def format_element(bfo, src, collection='VDB', rg=10, sf='year', so='a', of='gsblst'):
    """
    Give a list of recent publications by an author.
    
    src        = field to search the value of 035__a
    collection = collection to search
    rg         = number of formatted returns
    sf         = sort field
    so         = sort order (a/d)
    of         = output format
    """

    arg = {}
    if src == 'author':
      arg['p']  = "100:" + bfo.field('035__a') + ' OR ' + "700:" + bfo.field('035__a')
    else:
      arg['p']  = src + ":" + bfo.field('035__a')

    arg['cc'] = collection
    arg['rg'] = rg
    arg['so'] = so
    arg['sf'] = sf
    arg['of'] = of
    #try:
    res = perform_request_search(p=arg['p'], cc=arg['cc'], rg=arg['rg'], so=arg['so'], sf=arg['sf'])
    htmlstub = ''
    i = 0
    while i < rg:
       if len(res) > i:
          htmlstub += print_record(res[i], of)
       i += 1

    if len(res) > 0:
       htmlstub += '<p align="right">'
       htmlstub += '<a href="/search?sc=1&action_search=Search&p=' + arg['p'] + '">All known publications</a>'
       htmlstub += '</p><hr/>'
    return htmlstub

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0

def test_format(recID, src='980__a'):
    """
    only for testing of format
    """
    bfo = BibFormatObject(recID)
    print format_element(bfo, src)
 
if __name__ == '__main__': 
    test_format(recID = 2725)
    test_format(recID = 79809, src='536__0')
