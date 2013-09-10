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
Print json-structure of document types for authority records
@author: arwagner
"""
__revision__ = "$Id$"

try: import json
except ImportError: import simplejson as json


def format_element(bfo):
    """
    Print json-structure of document types for authority records
    """

    # get an array of hashes for the identifier fields

    m555 = []

    # copy subfields of 555, however, $5 has to end up in $2
    for field in bfo.fields('555'):
      reform = {}
      for sf in field:
        if sf == '5':
          reform['2'] = field['5']
        else:
          reform[sf] = field[sf]
      m555.append(reform)
      

    res  = []
    hgf  = {}

    hgf['a'] = bfo.fields('155__a')[0]
    hgf['0'] = bfo.fields('035__a')[0]
    hgf['2'] = "PUB:(DE-HGF)"
    hgf['m'] = bfo.fields('3367_m')[0]
    
    res.append(hgf)
    for r in m555:
      res.append(r)

    return(json.dumps(res, sort_keys=True, indent=2))

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
