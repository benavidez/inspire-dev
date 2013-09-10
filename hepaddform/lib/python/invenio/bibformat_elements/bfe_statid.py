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
Process StatID-fields (Marc 915) and display database coverage
@author: arwagner
"""
__revision__ = "$Id$"

def format_element(bfo, src, separator=' ; ', onlyfirst='no'):
    """
    Process StatID-fields (Marc 915) and display database coverage

    """

    # get an array of hashes for the identifier fields

    tag    = "915__"
    fields = bfo.fields(tag)
    ids    = []
    logos  = []
    
    imgnatli   = "http://images.opac.d-nb.de/hermes/search/logo_dfg.jpg"
    imgallianz = "http://images.opac.d-nb.de/hermes/search/logo_dfg.jpg"
    imgallianz = "http://k1www.gbv.de/images/logos/natliz_logo.jpg"
    imgOA      = "http://open-access.net/fileadmin/template/ipoa/img/logo_head.gif"

    for i in fields:
        if (i['a'] != 'DBCoverage') and (i['a'] != 'WoS'):
          if   i['0'] == 'StatID:(DE-HGF)0400':
            logos.append('<img src="' + imgallianz + '"alt="' + i['a'] + '">')
          elif i['0'] == 'StatID:(DE-HGF)0420':
            logos.append('<img src="' + imgnatli + '"alt="' + i['a'] + '">')
          elif (i['0'] == 'StatID:(DE-HGF)0010') or \
               (i['0'] == 'StatID:(DE-HGF)0020') or \
               (i['0'] == 'StatID:(DE-HGF)0030') or \
               (i['0'] == 'StatID:(DE-HGF)0040'):
            # old statistics keys, do not show them
            pass
          else:
            ids.append(i['a'])
        else:
          if i['0'] == 'StatID:(DE-HGF)0500':
            logos.append('<img src="' + imgOA + '"alt="' + i['b'] + '">')
          else:
            ids.append(i['b'])

    if onlyfirst == 'yes':
       return ids[0]
    else:
       return separator.join(ids + logos)

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
