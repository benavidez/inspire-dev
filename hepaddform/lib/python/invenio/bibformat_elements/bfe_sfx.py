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
Create a form that can trigger an OpenURL resolver like SFX.
@author: arwagner
"""
__revision__ = "$Id$"

from invenio.config import \
     CFG_LINKRESOLVER, \
     CFG_LINKRESOLVERICON

def format_element(bfo, src):
    """
    Construct the online linking box using SFX
    """


    if CFG_LINKRESOLVER == '':
      return ''

    # get an array of hashes for the identifier fields
    issns = bfo.fields("022__$a")

    frm = ''
    if len(issns) > 0:
       # Generate a form to send user input to SFX, use the first ISSN
       # as journal identifier. This form is only generated if we have
       # an ISSN
       frm = "<p>"
       frm = frm + "  <!-- Hook up with SFX -->\n";
       frm = frm + '<form method="GET" action="' + CFG_LINKRESOLVER + '" name="resolve" target="newwin">'
       frm = frm + "<fieldset>\n";
       frm = frm + '<input type="hidden" name="rft.issn" value="' + issns[0] + '">'
       frm = frm + '<input type="hidden" name="url_ver" value="Z39.88-2004">'
       frm = frm + '  <table><tr>'
       frm = frm + '  <td><label for="rft.volume">Vol.: </label></td><td><input type="text" id="rft.volume" name="rft.volume" value="" size="10"></td>'
       frm = frm + '  <td><label for="rft.issue" >Iss.: </label></td><td><input type="text" id="rft.issue"  name="rft.issue"  value="" size="10"></td>'
       frm = frm + '  <td><label for="rft.year"  >Year: </label></td><td><input type="text" id="rft.year"   name="rft.year"   value="" size="10"></td>'
       frm = frm + '  <td><label for="rft.spage" >Page: </label></td><td><input type="text" id="rft.spage"  name="rft.spage"  value="" size="10"></td>'
       frm = frm + '  <td><input type="image" src="' + CFG_LINKRESOLVERICON +'" alt="GO"></td>'
       frm = frm + '  </tr></table>'
       frm = frm + "</fieldset>\n";
       frm = frm + '</form>'
       frm = frm + '</p>'

    return frm

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
