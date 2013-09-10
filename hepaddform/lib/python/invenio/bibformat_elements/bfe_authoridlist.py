# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2011-2012, HGF
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

def format_element(bfo, firstautag='100%%', otherautag='700%%', separator=' ; '):
    """
    Give a list of all authors of the current record together with their
    ID numbers if they are linked in $0 subfield

    """

    # get an array of hashes for the fields
    firstau   = bfo.fields(firstautag)
    otherau   = bfo.fields(otherautag)

    aulist = []

    name = firstau[0]['a']
    # pythonic if (not(defined())
    try: 
       name = name + " [" + firstau[0]['0'] + "]"
    except:
       pass
    aulist.append(name)

    for au in otherau:
        name = au['a']
        try: 
           name = name + " [" + au['0'] + "]"
        except:
           pass
        aulist.append(name)

    return separator.join(aulist)

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
