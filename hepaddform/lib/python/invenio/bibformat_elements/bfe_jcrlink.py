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
Generate a link to JCR in case a JRC name is within the records ID
numbers.
@author: arwagner
"""
__revision__ = "$Id$"

def format_element(bfo):
    """
    Generate a link to JCR in case a JRC name is within the records ID
    """

    # get an array of hashes for the identifier fields

    src        = 'JCR'
    tag        = '0247_'
    subfield   = '2'
    search     = 'JCR:'
    replace    = ''
    printfield = 'a'

    fields = bfo.fields(tag)
    ids    = []
    
    base = 'http://admin-apps.webofknowledge.com/JCR/JCR?RQ=RECORD&rank=1&journal='
    link = ''

    for i in fields:
        if i[subfield] == src:
           id = i[printfield]
           id = id.replace(search, replace) 
           id = id.replace(' ', '+')
           link = base + id
    
    if link != '':
       link = '<a href="' + link + '" title="Journal Citation Report">JCR</a>'

    return link

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
