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
"""BibFormat element - Prints a custom field
@author: arwagner
"""
__revision__ = "$Id$"

def format_element(bfo, tag='915__'):
    """
    Fetch a given identifier from the record

    @param tag: field to check for src. By default use 915__ according to Marc
    """

    # get an array of hashes for the identifier fields
    statids = bfo.fields(tag)
    jsstr = '['
    for statid in statids:
        id   = ""
        tit  = ""
        sub  = ""
        type = ""
        jsstr = jsstr + '{ '
        for key in statid:
            jsstr = jsstr + '\\"' + key + '\\"'
            jsstr = jsstr + ' : '
            jsstr = jsstr + '\\"' + statid.get(key) + '\\", '
        jsstr = jsstr + '}, '
    jsstr = jsstr + ']'

    return jsstr

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0

