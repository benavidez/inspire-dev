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
Use statistics fields from 915 to notify about open access
Also evaluates arXiv and pmc stanzas from 0247_
@author: arwagner
"""
__revision__ = "$Id$"

def format_element(bfo, src, separator=' ', onlyfirst='no'):
    """
    Process StatID-fields (Marc 915) and produce links thereof

    """

    # get an array of hashes for the identifier fields

    tag    = "915__"
    fields = bfo.fields(tag)
    logos  = []
    
    imgnatli   = "http://images.opac.d-nb.de/hermes/search/logo_dfg.jpg"
    imgallianz = "http://images.opac.d-nb.de/hermes/search/logo_dfg.jpg"
    imgallianz = "http://k1www.gbv.de/images/logos/natliz_logo.jpg"
    imgOA      = "http://upload.wikimedia.org/wikipedia/commons/5/57/Oa_80x15_orange.png"
    hasOA      = 0
    for i in fields:
        # if['0'] == 'StatID:(DE-HGF)0420':
        #   logos.append('<img src="' + imgnatli + '"alt="' + i['a'] + '">')
        if i['0'] == 'StatID:(DE-HGF)0500':
          logos.append('<img src="' + imgOA + '"alt=OpenAccess by "' + i['b'] + '">')
          hasOA = 1

    # We also have OA if we have a PMC ID or arXiv or ... ?
    tag    = "0247_"
    fields = bfo.fields(tag)
    for i in fields:
        if i['2'] == 'pmc':
          if hasOA == 0:
             logos.append('<img src="' + imgOA + '"alt=OpenAccess by "' + i['2'] + '">')
             hasOA = 1
        if i['2'] == 'arXiv':
          if hasOA == 0:
             logos.append('<img src="' + imgOA + '"alt=OpenAcces by "' + i['2'] + '">')
             hasOA = 1


    if onlyfirst == 'yes':
       return logos[0]
    else:
       return separator.join(logos)

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
