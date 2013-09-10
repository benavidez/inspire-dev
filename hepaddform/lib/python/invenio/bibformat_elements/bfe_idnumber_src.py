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
Fetch a given identifier from the record
@author: arwagner
"""
__revision__ = "$Id$"

def format_element(bfo, src, search="", replace="", subfield='2', tag='0247_', printfield='a', separator=' ; ', onlyfirst='yes'):
    """
    Fetch a given identifier from the record

    @param src: value in subfield to select
    @param search: value to replace by replace argument. Meant to strip of some text
    @param replace: replacement value
    @param subfield: subfield to search for src
    @param tag: field to check for src. By default use 0247_ according to Marc
    @printfield: subfield to print
    @param separator: a separator between keywords
    """

    # get an array of hashes for the identifier fields

    fields = bfo.fields(tag)
    ids    = []
    

    for i in fields:
        try:
           if src in i[subfield]:
              id = i[printfield] + ' <small>['+ i[subfield] + ']</small>'
              id = id.replace(search, replace) 
              ids.append( id )
        except:
          pass

    if onlyfirst == 'yes':
       try:
          return ids[0]
       except:
          return ""
    else:
       return separator.join(ids)
    #return separator.join(ids)


def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
