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
"""BibFormat element - 
Print grant information in JSON structure.
We need to follow some immediate top-elements to add data.
@author: arwagner
"""
__revision__ = "$Id$"
from invenio.bibformat_engine import BibFormatObject
from invenio.search_engine import \
  perform_request_search

import re
try: import json
except ImportError: import simplejson as json

## from urllib import quote, quote_plus
## from invenio.config import CFG_SITE_URL
## from invenio.urlutils import create_html_link

def format_element(bfo):
    """
    Fetch a given identifier from the record

    """

    recid      = bfo.field('035__a')
    rectitle   = bfo.field('150__a')
    rectime    = bfo.field('150__y')
              
    # Get the name of the immediate top. This is needed for the 9131_
    # field
    tag        = '550__'
    topbfo     = ''
    topid      = ''
    topname    = ''
    topshort   = ''
    toptopname = ''
    toptopid   = ''
    for field in bfo.fields(tag):
      if field['w'] == 't':
        topid   = field['0']
        topname = field['a']
        search  = '035__a:"' + topid + '"'
        res = perform_request_search(p=search)
    try:
       topbfo = BibFormatObject(res[0])
       # if we got an immediate top, extract it's name and id.
       for field in topbfo.fields(tag):
         if field['w'] == 't':
           toptopid   = field['0']
           toptopname = field['a']
       tag = '450__'
       for field in topbfo.fields(tag):
         if ('w' in field) and ('5' in field):
            if (field['w'] == 'd') and not ('5' in field):
             topshort += field['a'] + " - "
       topshort = re.sub(' - $', '', topshort)
    except:
      pass

    # Extract shortcuts from 450__$wd fields
    tag      = '450__'
    recshort = ''
    for field in bfo.fields(tag):
      if 'w' in field:
         if field['w'] == 'd':
           recshort += field['a'] + ", "
    recshort = re.sub(', $', '', recshort)

    # Extract grant identifiers
    tag      = '035__a'
    grantid  = ''
    grantid  = re.sub('G:\([^)]*\)', '', bfo.field(tag))

    # get the call idendfier from 372 (field of activity)
    call     = ''
    tag      = '372__'
    for field in bfo.fields(tag):
        call    = field['a']

    # Build up a hash which is later on dumped to a JSON
    res = {}
    res['label'] =''

    if topshort != '':
      res['label'] += topshort + ': ' 

    res['label'] += recshort + ' - '
    res['label'] += rectitle + ' ('

    # if we have an x subfield like POF I etc.
    if bfo.field('150__x') != '':
       res['label'] += bfo.field('150__x') + ": "
    res['label']  += rectime                            \
                   + ')'
    # build up 536, the usual grant field.
    res['I536__0'] = recid
    res['I536__a'] = recshort + " - " + rectitle
    if grantid != '':
      res['I536__a'] += ' (' + grantid + ')'
      res['I536__c'] = grantid
    if call != '':
      res['I536__f'] = call

    # 9131_ is reserved for HGF specific stuff. Only write it if the
    # funding bodies ID is I:(DE-588b)5165524-X ie. the HGF
    #if (bfo.field('5101_0') == 'I:(DE-588b)5165524-X'):
    res['I9131_0'] = recid
    res['I9131_a'] = 'DE-HGF'
    res['I9131_b'] = toptopname
    res['I9131_k'] = topshort
    res['I9131_l'] = topname
    res['I9131_v'] = rectitle

    # Get rid of empty elements as they are not allowed in Marc
    todel = []
    for r in res:
      if res[r] == '':
        todel.append(r)
    for r in todel: 
      del res[r]


    return json.dumps(res, sort_keys=True, indent=2)

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
    test_format(recID = 130111)
    test_format(recID = 79809)
    test_format(recID = 130113)
    test_format(recID = 130112)
    test_format(recID = 130092)


