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
Construct a link to full text using OpenURL Resolver
CFG_LINKRESOLVER and CFG_LINKRESOLVERICON
@author: arwagner
"""
__revision__ = "$Id$"

from invenio.config import \
     CFG_LINKRESOLVER, \
     CFG_LINKRESOLVERICON

def format_element(bfo, src):
    """
    Construct a link to full text using OpenURL Resolver
    CFG_LINKRESOLVER and CFG_LINKRESOLVERICON
    """

    # get an array of hashes for the identifier fields

    id      = bfo.fields("773__0")
    doi     = bfo.fields("773__a")
    py      = bfo.fields("773__y")
    vol     = bfo.fields("773__v")
    issue   = bfo.fields("773__n")
    page    = bfo.fields("773__p")
    journal = bfo.fields("773__t")
    issn    = bfo.fields("773__x")
    year    = bfo.fields("260__c")
    title   = bfo.fields("245%%a")


    try:
      # only execute if CFG_LINKRESOLVER is set and not ''
      CFG_LINKRESOLVER
      if CFG_LINKRESOLVER == '':
        return ''

      # Try to construct an OpenURL as far as possible
      openurl  = CFG_LINKRESOLVER
      openurl += '?ctx_ver=Z39.88-2004'
      
      # Usually, we have at least a title and a year, add this to common 
      # so that fields might be empty if we have nothing more
      common = ''
      try:
         common += '&rft.atitle='   + title[0].replace(' ', '+')
      except:
        pass
      try:
         common += '&rft.year='   + year[0]
      except:
        pass

      # Build up fields from structured data. This is the most usable
      # part of the openURL. Use emptyness of this part to trigger
      # Linkresolver display
      fields   = ''
      try:
        fields += '&rft_id=info:doi/' + doi[0]
      except:
        pass
      try:
         fields += '&rft.issn='   + issn[0]
      except:
        pass
      try:
         fields += '&rft.volume=' + vol[0]
      except:
        pass
      try:
         fields += '&rft.issue='  + issue[0]
      except:
        pass
      try:
         fields += '&rft.spage='  + page[0].split(' - ')[0]
      except:
        pass
      try:
         fields += '&rft.epage='  + page[0].split(' - ')[1]
      except:
        pass
      try:
         fields += '&rft.jtitle='  + journal[0].replace(' ', '+')
      except:
        pass

      link = ''
      # Only if we have structured data...
      if fields != '':
        link  = '<a href="' + openurl + fields + common + '">'
        link += '<img src="' + CFG_LINKRESOLVERICON + '" alt="GO">'
        link += '</a>'


      return link
    except:
      return ''

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
